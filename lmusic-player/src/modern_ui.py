#!/usr/bin/env python3
"""
Modern UI for the Python Music Player using CustomTkinter

Features:
- Dark theme with a minimalist layout
- Sidebar for Library / Playlists
- Now playing bar with album art, playback controls, interactive progress slider
- Add files, folders, scan directories
- Save / Load playlists (JSON)
- Metadata display using Mutagen; Album art shown with Pillow
- Background metadata scan to avoid UI freezes
"""

import os
import json
import threading
import time
import logging
from io import BytesIO

try:
    import customtkinter as ctk
    from tkinter import ttk
except Exception:
    ctk = None
    from tkinter import ttk
import tkinter as tk
from tkinter import filedialog, messagebox

from .player import MusicPlayer
from .config import APP_NAME, CONFIG_FILE, BASE_DIR, ICONS_DIR
from . import utils

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

logger = logging.getLogger(__name__)


class ModernMusicPlayerApp:
    def __init__(self, root=None):
        # If CustomTkinter is not available, raise an error asking user to install it
        if ctk is None:
            raise Exception("CustomTkinter is required for the modern UI. Install: pip install customtkinter")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = root or ctk.CTk()
        self.root.title(f"{APP_NAME} — Modern")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        # Load config
        self.config = utils.load_config(CONFIG_FILE)

        # Player backend
        self.player = MusicPlayer()
        try:
            self.player.set_volume(self.config.get('volume', 0.7))
        except Exception:
            pass

        # Build layout
        self._setup_layout()

        # Bind player callbacks
        self.player.on_song_change = self._on_song_change
        self.player.on_playback_end = self._on_playback_end

        # Update loop for UI
        self._updating = True
        self._schedule_update()

        # Load last playlist if configured
        try:
            last_pl = self.config.get('last_playlist')
            if last_pl and isinstance(last_pl, list):
                files = [f for f in last_pl if os.path.exists(f)]
                if files:
                    self.player.load_playlist(files)
                    self._refresh_playlist_ui()
                    idx = int(self.config.get('last_index', 0))
                    self.player.current_index = min(max(0, idx), len(files) - 1)
                    if self.config.get('resume_on_start'):
                        self.player.play(self.player.current_index)
                        self._refresh_playlist_ui()
        except Exception:
            pass

    def _setup_layout(self):
        # Overall grid: sidebar + main content
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=220)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=(12, 6), pady=12)
        self._build_sidebar()

        # Main Content
        self.content = ctk.CTkFrame(self.root)
        self.content.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=12)
        self._build_main_content()

        # Now Playing bar at bottom
        self.now_playing = ctk.CTkFrame(self.root, height=110)
        self.now_playing.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(6, 12))
        self._build_now_playing()
        # Menu
        self._build_menu()

    def _build_sidebar(self):
        ctk.CTkLabel(self.sidebar, text=APP_NAME, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(8, 18))

        self.btn_library = ctk.CTkButton(self.sidebar, text="Library", command=self._show_library)
        self.btn_library.pack(fill='x', padx=8, pady=6)
        self.btn_playlists = ctk.CTkButton(self.sidebar, text="Playlists", command=self._show_playlists)
        self.btn_playlists.pack(fill='x', padx=8, pady=6)

        ctk.CTkButton(self.sidebar, text="Add Files", command=self._add_files, fg_color="#27ae60").pack(fill='x', padx=8, pady=(18, 6))
        ctk.CTkButton(self.sidebar, text="Add Folder", command=self._add_folder, fg_color="#27ae60").pack(fill='x', padx=8, pady=6)

        # Library scan
        ctk.CTkButton(self.sidebar, text="Scan Library", command=self._scan_library).pack(fill='x', padx=8, pady=6)

        # Small controls
        self.search_var = ctk.StringVar()
        ctk.CTkEntry(self.sidebar, placeholder_text="Search", textvariable=self.search_var).pack(fill='x', padx=8, pady=(14, 6))
        ctk.CTkButton(self.sidebar, text="Settings", command=self._open_settings, fg_color="#1abc9c").pack(fill='x', padx=8, pady=(12, 3))

    def _build_main_content(self):
        # Header
        header = ctk.CTkFrame(self.content, height=48)
        header.pack(fill='x')
        self.header_label = ctk.CTkLabel(header, text="Library", font=ctk.CTkFont(size=16, weight="bold"))
        self.header_label.pack(side='left', padx=12, pady=12)

        # Content splitter: left for playlist list, right for metadata/album art
        body = ctk.CTkFrame(self.content)
        body.pack(fill='both', expand=True, pady=(12, 0))
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=0)

        # Playlist tree
        self.playlist_tree = ttk.Treeview(body, columns=("name", "artist", "duration"), show='headings', selectmode='browse')
        self.playlist_tree.heading('name', text='Title')
        self.playlist_tree.heading('artist', text='Artist')
        self.playlist_tree.heading('duration', text='Duration')
        self.playlist_tree.column('name', width=420)
        self.playlist_tree.column('artist', width=200)
        self.playlist_tree.column('duration', width=80, anchor='center')
        self.playlist_tree.bind('<Double-1>', self._on_playlist_double_click)

        scroll_y = ttk.Scrollbar(body, orient='vertical', command=self.playlist_tree.yview)
        self.playlist_tree.configure(yscrollcommand=scroll_y.set)
        self.playlist_tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')

        # Right side: album art and metadata
        side = ctk.CTkFrame(body, width=260)
        side.grid(row=0, column=2, sticky='nsew', padx=(12, 0))
        side.grid_rowconfigure(0, weight=0)
        side.grid_rowconfigure(1, weight=1)

        self.album_art_label = ctk.CTkLabel(side, text='No Art', corner_radius=8)
        self.album_art_label.pack(padx=12, pady=12)

        self.meta_title = ctk.CTkLabel(side, text='No song selected', font=ctk.CTkFont(size=14, weight='bold'))
        self.meta_title.pack(padx=12, pady=(6, 0))
        self.meta_artist = ctk.CTkLabel(side, text='', font=ctk.CTkFont(size=12))
        self.meta_artist.pack(padx=12, pady=(2, 12))

    def _build_now_playing(self):
        # Left: album art
        self.now_left = ctk.CTkFrame(self.now_playing, width=200)
        self.now_left.pack(side='left', padx=12, pady=10)
        self.now_art = ctk.CTkLabel(self.now_left, text='No Art', width=88, height=88, corner_radius=8)
        self.now_art.pack(padx=6, pady=6)

        # Middle: title/artist and progress
        self.now_middle = ctk.CTkFrame(self.now_playing)
        self.now_middle.pack(side='left', fill='both', expand=True, padx=12, pady=10)
        self.now_title_lbl = ctk.CTkLabel(self.now_middle, text='No song', font=ctk.CTkFont(size=14, weight='bold'))
        self.now_title_lbl.pack(anchor='w')
        self.now_artist_lbl = ctk.CTkLabel(self.now_middle, text='', font=ctk.CTkFont(size=12))
        self.now_artist_lbl.pack(anchor='w', pady=(0, 6))

        # Progress row
        self.progress_time_var = ctk.StringVar(value='0:00')
        self.total_time_var = ctk.StringVar(value='0:00')
        top_row = ctk.CTkFrame(self.now_middle)
        top_row.pack(fill='x')
        self.now_time_label = ctk.CTkLabel(top_row, textvariable=self.progress_time_var, width=40)
        self.now_time_label.pack(side='left')
        self.progress_slider = ctk.CTkSlider(self.now_middle, from_=0, to=100, number_of_steps=0, command=self._on_progress_slider)
        self.progress_slider.pack(fill='x', pady=(2, 0))
        self.now_total_label = ctk.CTkLabel(top_row, textvariable=self.total_time_var, width=40)
        self.now_total_label.pack(side='right')

        # Right: controls
        self.now_right = ctk.CTkFrame(self.now_playing, width=320)
        self.now_right.pack(side='right', padx=12, pady=10)

        self.prev_btn = ctk.CTkButton(self.now_right, text='⏮', command=self._previous)
        self.play_btn = ctk.CTkButton(self.now_right, text='▶', command=self._toggle_play)
        self.next_btn = ctk.CTkButton(self.now_right, text='⏭', command=self._next)
        self.prev_btn.pack(side='left', padx=6)
        self.play_btn.pack(side='left', padx=6)
        self.next_btn.pack(side='left', padx=6)

        # volume
        self.volume_var = tk.DoubleVar(value=self.player.volume * 100)
        self.volume_slider = ctk.CTkSlider(self.now_right, from_=0, to=100, number_of_steps=100, command=self._on_volume)
        self.volume_slider.set(self.player.volume * 100)

    def _build_menu(self):
        menubar = ctk.CTkFrame(self.root, fg_color='transparent')
        menubar.pack(fill='x')
        # Minimal menu as buttons in the top-left
        frame = ctk.CTkFrame(menubar, fg_color='transparent')
        frame.pack(side='left', padx=6, pady=4)
        ctk.CTkButton(frame, text='File', command=self._show_file_menu, width=80).pack(side='left', padx=6)
        ctk.CTkButton(frame, text='Settings', command=self._open_settings, width=80).pack(side='left', padx=6)

    def _show_file_menu(self):
        # Popup style menu using standard tkinter Menu for simplicity
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label='Load Playlist', command=lambda: self.load_playlist_from_file(filedialog.askopenfilename()))
        menu.add_command(label='Save Playlist', command=lambda: self.save_playlist(filedialog.asksaveasfilename(defaultextension='.json')))
        menu.add_separator()
        menu.add_command(label='Exit', command=self.quit)
        try:
            menu.tk_popup(self.root.winfo_rootx()+10, self.root.winfo_rooty()+30)
        finally:
            menu.grab_release()
        self.volume_slider.pack(side='left', padx=8)

    # ------------------ UI actions ------------------
    def _show_library(self):
        self.header_label.config(text='Library')

    def _show_playlists(self):
        self.header_label.config(text='Playlists')

    def _add_files(self):
        files = filedialog.askopenfilenames(filetypes=[('Audio files', '*.mp3 *.wav *.ogg *.flac *.m4a')])
        if files:
            self.player.add_files(files)
            self._refresh_playlist_ui()
            # Background metadata loader
            threading.Thread(target=self._load_metadata_background, args=(files,), daemon=True).start()

    def _add_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            filecount = self.player.add_folder(folder)
            self._refresh_playlist_ui()
            if filecount > 0:
                threading.Thread(target=self._load_metadata_background, args=([os.path.join(folder, f) for f in os.listdir(folder)],), daemon=True).start()

    def _scan_library(self):
        path = filedialog.askdirectory()
        if not path:
            return
        # Walk directory and gather audio files
        audio_files = []
        for root, _, files in os.walk(path):
            for f in files:
                if f.lower().endswith(('.mp3', '.wav', '.ogg', '.flac', '.m4a')):
                    audio_files.append(os.path.join(root, f))
        if audio_files:
            self.player.add_files(audio_files)
            self._refresh_playlist_ui()
            threading.Thread(target=self._load_metadata_background, args=(audio_files,), daemon=True).start()

    def _open_settings(self):
        # Minimal settings dialog using a Toplevel window
        try:
            w = ctk.CTkToplevel(self.root)
            w.title('Preferences')
            w.geometry('420x340')
            # Resume on start
            tk.Label(w, text='Resume playback on start:').pack(pady=(8, 2))
            resume_var = tk.BooleanVar(value=self.config.get('resume_on_start', False))
            tk.Checkbutton(w, variable=resume_var).pack()
            # Theme selection
            tk.Label(w, text='Theme:').pack(pady=(12, 2))
            theme_var = tk.StringVar(value=self.config.get('theme', 'dark'))
            tk.Radiobutton(w, text='Dark', variable=theme_var, value='dark').pack()
            tk.Radiobutton(w, text='Light', variable=theme_var, value='light').pack()
            # Crossfade setting
            tk.Label(w, text='Crossfade duration (ms):').pack(pady=(12, 2))
            cf_var = tk.IntVar(value=self.config.get('crossfade', 500))
            tk.Spinbox(w, from_=0, to=5000, increment=100, textvariable=cf_var).pack()
            # Save / Cancel
            btn_frame = tk.Frame(w)
            btn_frame.pack(pady=14)
            tk.Button(btn_frame, text='Save', command=lambda: self._save_settings(w, resume_var.get(), theme_var.get(), cf_var.get())).pack(side='left', padx=8)
            tk.Button(btn_frame, text='Cancel', command=w.destroy).pack(side='left', padx=8)
        except Exception as e:
            messagebox.showerror('Error', f'Could not open settings: {e}')

    def _save_settings(self, win, resume_on_start, theme='dark', crossfade_ms=500):
        self.config['resume_on_start'] = resume_on_start
        self.config['theme'] = theme
        self.config['crossfade'] = int(crossfade_ms)
        utils.save_config(CONFIG_FILE, self.config)
        # apply new theme and crossfade length
        try:
            self.apply_theme(theme)
        except Exception:
            pass
        win.destroy()

    def _load_metadata_background(self, files):
        for f in files:
            try:
                # cause player to compute song length and metadata
                self.player.get_song_length(f)
            except Exception:
                pass
        # once loaded refresh UI
        self.root.after(10, self._refresh_playlist_ui)

    def _refresh_playlist_ui(self):
        # Clear tree
        for item in self.playlist_tree.get_children():
            self.playlist_tree.delete(item)
        for i, fpath in enumerate(self.player.playlist):
            info = self.player.get_current_song_info() if i == self.player.current_index else None
            if info and i == self.player.current_index:
                name = info.get('title', os.path.basename(fpath))
                artist = info.get('artist', '')
                dur = utils.format_time(info.get('length', 0))
            else:
                name = os.path.basename(fpath)
                artist = ''
                dur = utils.format_time(self.player.get_song_length(fpath))
            self.playlist_tree.insert('', 'end', iid=str(i), values=(name, artist, dur))
        # highlight current
        if 0 <= self.player.current_index < len(self.player.playlist):
            try:
                self.playlist_tree.selection_set(str(self.player.current_index))
                self.playlist_tree.see(str(self.player.current_index))
            except Exception:
                pass

    # Playlist interactions
    def _on_playlist_double_click(self, event):
        sel = self.playlist_tree.selection()
        if sel:
            idx = int(sel[0])
            self.player.current_index = idx
            try:
                self.player.play(idx)
                self._refresh_playlist_ui()
            except Exception as e:
                messagebox.showerror('Playback Error', str(e))

    # Now playing interactions
    def _toggle_play(self):
        if not self.player.playlist:
            return
        if self.player.paused:
            self.player.unpause()
            self.play_btn.configure(text='⏸')
        elif not self.player.is_playing:
            self.player.play(self.player.current_index)
            self.play_btn.configure(text='⏸')
        else:
            self.player.pause()
            self.play_btn.configure(text='▶')
        self._refresh_playlist_ui()

    def _next(self):
        try:
            self.player.next()
            self._refresh_playlist_ui()
        except Exception as e:
            messagebox.showerror('Playback Error', str(e))

    def _previous(self):
        try:
            self.player.previous()
            self._refresh_playlist_ui()
        except Exception as e:
            messagebox.showerror('Playback Error', str(e))

    def _on_progress_slider(self, val):
        # Seek approximate using restart method
        if not self.player.is_playing:
            return
        try:
            percent = float(val)/100.0
            length = self.player.song_length
            new_pos = percent * length
            # Try to seek using player if supported
            try:
                if not self.player.is_playing:
                    self.player.play(self.player.current_index, start_pos=new_pos)
                else:
                    self.player.play(self.player.current_index, start_pos=new_pos)
                self._refresh_playlist_ui()
            except Exception:
                # Fallback (restart without precise seeking)
                self.player.stop()
                self.player.play(self.player.current_index)
        except Exception as e:
            logger.warning(f"Seek error: {e}")

    def _on_volume(self, val):
        try:
            vol = float(val)/100.0
            self.player.set_volume(vol)
        except Exception as e:
            logger.warning(f"Volume change error: {e}")

    def _on_song_change(self, song_info):
        if not song_info:
            return
        self.now_title_lbl.configure(text=song_info.get('title', ''))
        self.now_artist_lbl.configure(text=song_info.get('artist', ''))
        self.meta_title.configure(text=song_info.get('title', ''))
        self.meta_artist.configure(text=song_info.get('artist', ''))
        # album art
        try:
            art = self._extract_album_art(song_info.get('file_path'))
            if art:
                img = Image.open(BytesIO(art)).resize((160, 160))
                photo = ImageTk.PhotoImage(img)
                self.now_art.configure(image=photo)
                self.now_art.image = photo
                self.album_art_label.configure(image=photo)
                self.album_art_label.image = photo
            else:
                self.now_art.configure(text='No Art')
                self.album_art_label.configure(text='No Art')
        except Exception:
            pass

        # Update progress/total labels
        self.total_time_var.set(utils.format_time(song_info.get('length', 0)))
        # Set artwork and title
        try:
            # Ensure we set a small icon for now bar
            self.now_art.configure(text='')
        except Exception:
            pass

    def _on_playback_end(self):
        # automatically play next
        try:
            self.player.next()
            self._refresh_playlist_ui()
        except Exception:
            pass

    def _schedule_update(self):
        try:
            if self.player.is_playing:
                pos = self.player.get_current_position()
                # compute percent
                length = self.player.song_length
                if length > 0:
                    percent = (pos / length) * 100
                    self.progress_slider.set(percent)
                    self.progress_time_var.set(utils.format_time(pos))
            if self._updating:
                self.root.after(200, self._schedule_update)
        except Exception:
            if self._updating:
                self.root.after(200, self._schedule_update)

    def _extract_album_art(self, file_path):
        try:
            if Image is None:
                return None
            from mutagen import File as MutFile
            audio = MutFile(file_path)
            data = None
            if audio is None:
                return None
            # MP3 ID3APIC
            if 'APIC:' in audio.tags:
                data = audio.tags['APIC:'].data
            else:
                # flac
                pics = getattr(audio, 'pictures', None)
                if pics and len(pics) > 0:
                    data = pics[0].data
            return data
        except Exception:
            return None

    def save_playlist(self, filename):
        try:
            pl = {'name': os.path.basename(filename), 'files': list(self.player.playlist)}
            os.makedirs(os.path.join(BASE_DIR, 'playlists'), exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(pl, f, indent=2)
        except Exception as e:
            messagebox.showerror('Error', f'Could not save playlist: {e}')

    def load_playlist_from_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                pl = json.load(f)
            files = [f for f in pl.get('files', []) if os.path.exists(f)]
            self.player.load_playlist(files)
            self._refresh_playlist_ui()
        except Exception as e:
            messagebox.showerror('Error', f'Could not load playlist: {e}')

    def quit(self):
        self._updating = False
        self.config['volume'] = self.player.volume
        self.config['last_playlist'] = list(self.player.playlist)
        self.config['last_index'] = self.player.current_index
        utils.save_config(CONFIG_FILE, self.config)
        try:
            self.player.shutdown()
        except Exception:
            pass
        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass

    # hovered: convenience wrappers
    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.quit()

def run_modern_app():
    if ctk is None:
        print('CustomTkinter is required for the modern UI. pip install customtkinter')
        return
    app = ModernMusicPlayerApp()
    app.run()

if __name__ == '__main__':
    run_modern_app()
