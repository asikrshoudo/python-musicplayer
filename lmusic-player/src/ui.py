#!/usr/bin/env python3
"""
User interface for Python Music Player using Tkinter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import time
#!/usr/bin/env python3
"""
User interface for Python Music Player using Tkinter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import time
try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

from player import MusicPlayer
from config import BASE_DIR, ASSETS_DIR, ICONS_DIR, CONFIG_FILE, APP_NAME
import utils


class MusicPlayerApp:
    def __init__(self):
        """Initialize the music player application"""
        self.root = tk.Tk()

        # Load configuration (volume, theme, etc.)
        self.config = utils.load_config(CONFIG_FILE)

        self.setup_window()
        self.player = MusicPlayer()
        # Apply saved volume to player
        try:
            initial_volume = float(self.config.get('volume', self.player.volume))
            self.player.set_volume(initial_volume)
        except Exception:
            pass

        self.setup_player_callbacks()
        self.setup_ui()
        self.setup_bindings()

        # UI state
        self.updating_progress = False
        self.dragging_progress = False

        print("UI initialized successfully")

    def setup_window(self):
        """Configure main window"""
        # Use configured application name
        self.root.title(f"{APP_NAME} 🎵")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)
        self.root.configure(bg='#2c3e50')

        # Set window icon (if available)
        try:
            icon_path = os.path.join(ICONS_DIR, 'icon.png')
            if os.path.exists(icon_path):
                icon = ImageTk.PhotoImage(Image.open(icon_path))
                self.root.iconphoto(True, icon)
        except Exception as e:
            print(f"Could not load window icon: {e}")

        # Center window on screen
        self.center_window()

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_player_callbacks(self):
        """Setup callbacks for player events"""
        self.player.on_song_change = self.on_song_change
        self.player.on_playback_end = self.on_playback_end

    def setup_ui(self):
        """Setup user interface components"""
        # Menu first (for keyboard accelerators)
        self.create_menu()
        self.create_title_bar()
        self.create_song_info()
        self.create_progress_bar()
        self.create_controls()
        self.create_playlist()
        self.create_status_bar()

        # Ensure UI volume control matches player
        try:
            self.volume_var.set(self.player.volume * 100)
        except Exception:
            pass

    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Add Files...", command=self.add_files, accelerator="Ctrl+O")
        file_menu.add_command(label="Add Folder...", command=self.add_folder, accelerator="Ctrl+Shift+O")
        file_menu.add_separator()
        file_menu.add_command(label="Load Playlist...", command=self.load_playlist_dialog)
        file_menu.add_command(label="Save Playlist...", command=self.save_playlist_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        # Theme menu
        theme_menu = tk.Menu(menubar, tearoff=0)
        theme_menu.add_radiobutton(label='Dark', command=lambda: self.apply_theme('dark'))
        theme_menu.add_radiobutton(label='Light', command=lambda: self.apply_theme('light'))
        menubar.add_cascade(label='Theme', menu=theme_menu)

        # Attach menu
        self.root.config(menu=menubar)

        # Bind accelerators
        self.root.bind_all('<Control-o>', lambda e: self.add_files())
        self.root.bind_all('<Control-Shift-O>', lambda e: self.add_folder())
        self.root.bind_all('<Control-q>', lambda e: self.quit_app())

        # Apply saved theme
        theme = self.config.get('theme', 'dark')
        self.apply_theme(theme)

    def apply_theme(self, theme_name: str):
        """Apply a theme by name (basic color override)"""
        # Keep a minimal theme system: dark/light
        try:
            if theme_name == 'light':
                bg = '#ecf0f1'
                fg = '#2c3e50'
                header = '#bdc3c7'
                control_bg = '#3498db'
            else:
                bg = '#2c3e50'
                fg = '#ecf0f1'
                header = '#34495e'
                control_bg = '#3498db'

            self.root.configure(bg=bg)
            # Update top-level widgets where possible
            for widget in [self.root]:
                try:
                    widget.configure(bg=bg)
                except Exception:
                    pass

            # Update controls
            try:
                self.song_var.set(self.song_var.get())
                # We'll update player widgets colors (best effort)
                self.play_btn.configure(bg=control_bg, fg='white')
            except Exception:
                pass

            # Update playlist & other frames
            try:
                self.playlist_tree.configure(background=bg, foreground=fg)
            except Exception:
                pass

            # Save theme to config
            self.config['theme'] = theme_name
        except Exception:
            pass

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", f"{APP_NAME}\nA lightweight Python music player")

    def create_title_bar(self):
        """Create title bar"""
        title_frame = tk.Frame(self.root, bg='#34495e', height=60)
        title_frame.pack(fill='x', padx=10, pady=10)
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame,
                              text="🎵 Python Music Player",
                              font=('Arial', 18, 'bold'),
                              bg='#34495e',
                              fg='white')
        title_label.pack(side='left', padx=15, pady=15)

        # Version info
        version_label = tk.Label(title_frame,
                                text="v1.0.0",
                                font=('Arial', 10),
                                bg='#34495e',
                                fg='#bdc3c7')
        version_label.pack(side='right', padx=15, pady=15)

    def create_song_info(self):
        """Create current song info display"""
        info_frame = tk.Frame(self.root, bg='#2c3e50')
        info_frame.pack(fill='x', padx=20, pady=15)

        # Song title
        self.song_var = tk.StringVar(value="No song selected")
        song_label = tk.Label(info_frame,
                              textvariable=self.song_var,
                              font=('Arial', 14, 'bold'),
                              bg='#2c3e50',
                              fg='#ecf0f1',
                              wraplength=500)
        song_label.pack(pady=(0, 5))

        # Artist
        self.artist_var = tk.StringVar(value="")
        artist_label = tk.Label(info_frame,
                                textvariable=self.artist_var,
                                font=('Arial', 12),
                                bg='#2c3e50',
                                fg='#bdc3c7')
        artist_label.pack()

    def create_progress_bar(self):
        """Create progress bar and time display"""
        progress_frame = tk.Frame(self.root, bg='#2c3e50')
        progress_frame.pack(fill='x', padx=20, pady=15)

        # Time labels frame
        time_frame = tk.Frame(progress_frame, bg='#2c3e50')
        time_frame.pack(fill='x', pady=(0, 5))

        self.current_time_var = tk.StringVar(value="0:00")
        self.total_time_var = tk.StringVar(value="0:00")

        tk.Label(time_frame,
                 textvariable=self.current_time_var,
                 bg='#2c3e50',
                 fg='#bdc3c7',
                 font=('Arial', 10)).pack(side='left')

        tk.Label(time_frame,
                 textvariable=self.total_time_var,
                 bg='#2c3e50',
                 fg='#bdc3c7',
                 font=('Arial', 10)).pack(side='right')

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(progress_frame,
                                     variable=self.progress_var,
                                     from_=0, to=100,
                                     orient='horizontal',
                                     command=self.on_progress_drag)
        self.progress_bar.pack(fill='x')

        # Bind events for progress bar
        self.progress_bar.bind('<ButtonPress-1>', self.on_progress_press)
        self.progress_bar.bind('<ButtonRelease-1>', self.on_progress_release)

    def create_controls(self):
        """Create control buttons"""
        control_frame = tk.Frame(self.root, bg='#2c3e50')
        control_frame.pack(pady=20)

        # Control buttons style
        btn_style = {
            'bg': '#3498db',
            'fg': 'white',
            'font': ('Arial', 11, 'bold'),
            'relief': 'flat',
            'width': 12,
            'height': 1,
            'bd': 0
        }

        # Previous button
        tk.Button(control_frame,
                  text="⏮ Previous",
                  command=self.previous_song,
                  **btn_style).pack(side='left', padx=8)

        # Play/Pause button
        self.play_btn = tk.Button(control_frame,
                                  text="▶ Play",
                                  command=self.toggle_play,
                                  **btn_style)
        self.play_btn.pack(side='left', padx=8)

        # Next button
        tk.Button(control_frame,
                  text="⏭ Next",
                  command=self.next_song,
                  **btn_style).pack(side='left', padx=8)

        # Stop button
        tk.Button(control_frame,
                  text="⏹ Stop",
                  command=self.stop_music,
                  **{**btn_style, 'bg': '#e74c3c'}).pack(side='left', padx=8)

        # Volume control frame
        volume_frame = tk.Frame(self.root, bg='#2c3e50')
        volume_frame.pack(pady=15)

        tk.Label(volume_frame,
                 text="Volume:",
                 bg='#2c3e50',
                 fg='white',
                 font=('Arial', 10)).pack(side='left', padx=(0, 10))

        self.volume_var = tk.DoubleVar(value=self.player.volume * 100)
        volume_scale = ttk.Scale(volume_frame,
                                variable=self.volume_var,
                                from_=0, to=100,
                                orient='horizontal',
                                command=self.on_volume_change)
        volume_scale.pack(side='left')
        volume_scale.set(self.player.volume * 100)
        
        # Mute/unmute button
        self.mute_btn = tk.Button(volume_frame,
                      text="🔊",
                      command=self.toggle_mute,
                      bg='#95a5a6',
                      fg='white')
        self.mute_btn.pack(side='left', padx=(10, 0))

    def create_playlist(self):
        """Create playlist display"""
        playlist_frame = tk.Frame(self.root, bg='#2c3e50')
        playlist_frame.pack(fill='both', expand=True, padx=20, pady=15)

        # Playlist header
        header_frame = tk.Frame(playlist_frame, bg='#34495e')
        header_frame.pack(fill='x', pady=(0, 10))

        tk.Label(header_frame,
                 text="Playlist",
                 bg='#34495e',
                 fg='white',
                 font=('Arial', 13, 'bold')).pack(side='left', padx=10, pady=8)

        # Playlist buttons
        btn_frame = tk.Frame(header_frame, bg='#34495e')
        btn_frame.pack(side='right', padx=10, pady=5)

        tk.Button(btn_frame,
                  text="📁 Add Files",
                  command=self.add_files,
                  bg='#27ae60',
                  fg='white',
                  font=('Arial', 9),
                  relief='flat').pack(side='left', padx=3)

        tk.Button(btn_frame,
                  text="📂 Add Folder",
                  command=self.add_folder,
                  bg='#27ae60',
                  fg='white',
                  font=('Arial', 9),
                  relief='flat').pack(side='left', padx=3)

        tk.Button(btn_frame,
                  text="🗑 Clear",
                  command=self.clear_playlist,
                  bg='#e74c3c',
                  fg='white',
                  font=('Arial', 9),
                  relief='flat').pack(side='left', padx=3)

        tk.Button(btn_frame,
                  text="➖ Remove",
                  command=self.remove_selected,
                  bg='#f39c12',
                  fg='white',
                  font=('Arial', 9),
                  relief='flat').pack(side='left', padx=3)

        # Move up/down buttons
        tk.Button(btn_frame,
              text="⬆ Move Up",
              command=self.move_up,
              bg='#7f8c8d',
              fg='white',
              font=('Arial', 9),
              relief='flat').pack(side='left', padx=3)
        tk.Button(btn_frame,
              text="⬇ Move Down",
              command=self.move_down,
              bg='#7f8c8d',
              fg='white',
              font=('Arial', 9),
              relief='flat').pack(side='left', padx=3)

        # Playlist listbox with scrollbar
        listbox_frame = tk.Frame(playlist_frame, bg='#2c3e50')
        listbox_frame.pack(fill='both', expand=True)

        # Create treeview for better display
        columns = ('name', 'duration')
        self.playlist_tree = ttk.Treeview(listbox_frame,
                                         columns=columns,
                                         show='headings',
                                         selectmode='browse')

        # Configure columns
        self.playlist_tree.heading('name', text='Song Name')
        self.playlist_tree.heading('duration', text='Duration')
        self.playlist_tree.column('name', width=400, anchor='w')
        self.playlist_tree.column('duration', width=80, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(listbox_frame,
                                  orient='vertical',
                                  command=self.playlist_tree.yview)
        self.playlist_tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.playlist_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Bind double-click to play
        self.playlist_tree.bind('<Double-1>', self.on_playlist_double_click)
        # Right-click context menu for playlist
        self.playlist_tree.bind('<Button-3>', self.on_playlist_right_click)

        # Context menu
        self.playlist_context_menu = tk.Menu(self.root, tearoff=0)
        self.playlist_context_menu.add_command(label='Play', command=self.play_selected)
        self.playlist_context_menu.add_command(label='Remove', command=self.remove_selected)
        self.playlist_context_menu.add_separator()
        self.playlist_context_menu.add_command(label='Reveal in File Manager', command=self.reveal_selected)

    def create_status_bar(self):
        """Create status bar"""
        self.status_var = tk.StringVar(value="Ready - Add some music to get started!")
        status_bar = tk.Label(self.root,
                              textvariable=self.status_var,
                              relief='sunken',
                              anchor='w',
                              bg='#34495e',
                              fg='#bdc3c7',
                              font=('Arial', 9))
        status_bar.pack(side='bottom', fill='x')

    def setup_bindings(self):
        """Setup keyboard bindings"""
        # Global bindings
        self.root.bind('<space>', lambda e: self.toggle_play())
        self.root.bind('<Right>', lambda e: self.next_song())
        self.root.bind('<Left>', lambda e: self.previous_song())
        self.root.bind('<Escape>', lambda e: self.stop_music())
        self.root.bind('<Control-q>', lambda e: self.quit_app())
        self.root.bind('<Delete>', lambda e: self.remove_selected())

        # Window close event
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        # Start progress updater
        self.update_progress()

        # Start event checker
        self.check_music_events()
        # If config has last playlist and resume_on_start, attempt to load and play
        try:
            if self.config.get('last_playlist'):
                last_pl = self.config.get('last_playlist')
                if last_pl and isinstance(last_pl, list):
                    # Filter to files that exist
                    files = [f for f in last_pl if os.path.exists(f)]
                    if files:
                        self.player.load_playlist(files)
                        self.update_playlist_display()
                        last_index = int(self.config.get('last_index', 0))
                        if 0 <= last_index < len(self.player.playlist):
                            self.player.current_index = last_index
                        if self.config.get('resume_on_start'):
                            try:
                                self.player.play(self.player.current_index)
                                self.update_playlist_display()
                            except Exception:
                                pass
        except Exception:
            pass

    def on_playlist_double_click(self, event):
        """Handle double-click on playlist item"""
        selection = self.playlist_tree.selection()
        if selection:
            index = self.playlist_tree.index(selection[0])
            self.player.current_index = index
            self.play_music()

    def on_playlist_right_click(self, event):
        """Show context menu on right-click"""
        selection = self.playlist_tree.identify_row(event.y)
        if selection:
            self.playlist_tree.selection_set(selection)
            try:
                self.playlist_context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.playlist_context_menu.grab_release()

    def play_selected(self):
        """Play currently selected playlist item"""
        selection = self.playlist_tree.selection()
        if selection:
            index = self.playlist_tree.index(selection[0])
            self.player.current_index = index
            self.play_music()

    def save_playlist_dialog(self):
        """Save current playlist to an M3U file"""
        if not self.player.playlist:
            messagebox.showinfo('Save Playlist', 'Playlist is empty')
            return
        path = filedialog.asksaveasfilename(defaultextension='.m3u', filetypes=[('Playlist files', '*.m3u'), ('All files', '*.*')])
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write('#EXTM3U\n')
                    for p in self.player.playlist:
                        f.write(p + '\n')
                self.status_var.set(f"Saved playlist: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror('Error', f'Could not save playlist: {e}')

    def load_playlist_dialog(self):
        """Load an M3U playlist and replace current playlist"""
        path = filedialog.askopenfilename(filetypes=[('Playlist files', '*.m3u'), ('All files', '*.*')])
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    # Only keep existing files
                    files = [l for l in lines if os.path.exists(l)]
                    count = self.player.load_playlist(files)
                    self.update_playlist_display()
                    self.status_var.set(f"Loaded playlist: {count} files from {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror('Error', f'Could not load playlist: {e}')

    def reveal_selected(self):
        """Open the containing folder of the selected audio file (no-op in tests)"""
        selection = self.playlist_tree.selection()
        if selection:
            index = self.playlist_tree.index(selection[0])
            file_path = self.player.playlist[index]
            try:
                import subprocess
                if os.name == 'nt':
                    os.startfile(os.path.dirname(file_path))
                else:
                    subprocess.run(['xdg-open', os.path.dirname(file_path)])
            except Exception as e:
                print(f"Reveal error: {e}")

    def add_files(self):
        """Add files to playlist"""
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[
                ("All Supported Formats", "*.mp3 *.wav *.ogg *.m4a *.flac"),
                ("MP3 Files", "*.mp3"),
                ("WAV Files", "*.wav"),
                ("OGG Files", "*.ogg"),
                ("FLAC Files", "*.flac"),
                ("M4A Files", "*.m4a"),
                ("All Files", "*.*")
            ]
        )

        if files:
            try:
                # Add to playlist immediately to avoid UI lag, and load metadata in background
                count = self.player.add_files(files)
                self.update_playlist_display()
                self.status_var.set(f"✅ Added {count} files to playlist")

                # Spawn background thread to fetch metadata (length/title/artist) without blocking UI
                import threading
                def fetch_metadata(paths):
                    for p in paths:
                        try:
                            length = self.player.get_song_length(p)
                            # Update UI for the entry if it is displayed
                            self.root.after(10, self.update_playlist_display)
                        except Exception:
                            pass
                t = threading.Thread(target=fetch_metadata, args=(files,), daemon=True)
                t.start()
            except Exception as e:
                messagebox.showerror("Error", f"Could not add files: {e}")

    def add_folder(self):
        """Add folder to playlist"""
        folder = filedialog.askdirectory(title="Select Folder with Audio Files")
        if folder:
            try:
                count = self.player.add_folder(folder)
                self.update_playlist_display()
                self.status_var.set(f"✅ Added {count} files from folder")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def clear_playlist(self):
        """Clear playlist"""
        if messagebox.askyesno("Confirm", "Clear entire playlist?"):
            self.player.clear_playlist()
            self.update_playlist_display()
            self.song_var.set("No song selected")
            self.artist_var.set("")
            self.status_var.set("Playlist cleared")

    def remove_selected(self):
        """Remove selected song from playlist"""
        selection = self.playlist_tree.selection()
        if selection:
            index = self.playlist_tree.index(selection[0])
            if self.player.remove_from_playlist(index):
                self.update_playlist_display()
                self.status_var.set("Removed song from playlist")

    def move_up(self):
        """Move selected item up in the playlist"""
        selection = self.playlist_tree.selection()
        if not selection:
            return
        index = self.playlist_tree.index(selection[0])
        if index <= 0:
            return
        self.player.playlist[index - 1], self.player.playlist[index] = self.player.playlist[index], self.player.playlist[index - 1]
        self.update_playlist_display()
        self.playlist_tree.selection_set(self.playlist_tree.get_children()[index - 1])

    def move_down(self):
        """Move selected item down in the playlist"""
        selection = self.playlist_tree.selection()
        if not selection:
            return
        index = self.playlist_tree.index(selection[0])
        if index >= len(self.player.playlist) - 1:
            return
        self.player.playlist[index + 1], self.player.playlist[index] = self.player.playlist[index], self.player.playlist[index + 1]
        self.update_playlist_display()
        self.playlist_tree.selection_set(self.playlist_tree.get_children()[index + 1])

    def update_playlist_display(self):
        """Update the playlist treeview display"""
        # Clear current display
        for item in self.playlist_tree.get_children():
            self.playlist_tree.delete(item)

        # Add all songs to treeview
        for i, file_path in enumerate(self.player.playlist):
            song_info = self.player.get_current_song_info() if i == self.player.current_index else None

            if song_info and i == self.player.current_index:
                display_name = song_info['title']
                duration = utils.format_time(song_info['length'])
            else:
                display_name = os.path.basename(file_path)
                # Get duration for this file
                duration = utils.format_time(self.player.get_song_length(file_path))

            self.playlist_tree.insert('', 'end', values=(display_name, duration))

        # Highlight currently playing song
        if self.player.playlist and 0 <= self.player.current_index < len(self.player.playlist):
            items = self.playlist_tree.get_children()
            if items and self.player.current_index < len(items):
                self.playlist_tree.selection_set(items[self.player.current_index])
                self.playlist_tree.see(items[self.player.current_index])

    def play_music(self):
        """Play selected music"""
        try:
            if self.player.play():
                self.config['last_index'] = self.player.current_index
                self.config['last_playlist'] = list(self.player.playlist)
                self.update_playlist_display()
                self.play_btn.config(text="⏸ Pause")
                self.status_var.set("Now playing")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set(f"Error: {e}")

    def toggle_play(self):
        """Toggle play/pause"""
        if not self.player.playlist:
            messagebox.showwarning("Warning", "No songs in playlist! Add some music first.")
            return

        if self.player.paused:
            self.player.unpause()
            self.play_btn.config(text="⏸ Pause")
            self.status_var.set("Playback resumed")
        else:
            if not self.player.is_playing:
                self.play_music()
            else:
                self.player.pause()
                self.play_btn.config(text="▶ Play")
                self.status_var.set("Playback paused")

    def toggle_mute(self):
        """Toggle mute/unmute UI and player"""
        try:
            self.player.toggle_mute()
            if self.player.muted:
                self.mute_btn.config(text='🔈')
                self.status_var.set('Muted')
            else:
                self.mute_btn.config(text='🔊')
                self.status_var.set('Unmuted')
        except Exception as e:
            print(f"Mute toggle error: {e}")

    def stop_music(self):
        """Stop music playback"""
        self.player.stop()
        self.play_btn.config(text="▶ Play")
        self.progress_var.set(0)
        self.current_time_var.set("0:00")
        self.status_var.set("Playback stopped")

    def next_song(self):
        """Play next song"""
        if self.player.next():
            self.update_playlist_display()
            self.status_var.set("Next song")

    def previous_song(self):
        """Play previous song"""
        if self.player.previous():
            self.update_playlist_display()
            self.status_var.set("Previous song")

    def on_song_change(self, song_info):
        """Callback when song changes"""
        if song_info:
            self.song_var.set(song_info['title'])
            self.artist_var.set(song_info['artist'])

            # Update total time display
            total_time = utils.format_time(song_info['length'])
            self.total_time_var.set(total_time)

    def on_playback_end(self):
        """Callback when playback ends naturally"""
        print("Playback ended, playing next song...")
        self.next_song()

    def on_volume_change(self, value):
        """Handle volume change"""
        try:
            volume = float(value) / 100.0
            self.player.set_volume(volume)
        except ValueError:
            pass

    def on_progress_press(self, event):
        """Handle progress bar press"""
        self.dragging_progress = True

    def on_progress_release(self, event):
        """Handle progress bar release"""
        if self.dragging_progress and self.player.is_playing:
            # Seek to new position (basic implementation)
            progress = self.progress_var.get() / 100.0
            new_position = progress * self.player.song_length

            # Note: PyGame doesn't support precise seeking well
            # This is a basic implementation that restarts the song
            try:
                self.player.stop()
                self.player.play()
                # The position can't be precisely set with PyGame's mixer
            except Exception as e:
                print(f"Seek error: {e}")

        self.dragging_progress = False

    def on_progress_drag(self, value):
        """Handle progress bar dragging"""
        if self.dragging_progress and self.player.song_length > 0:
            position = (float(value) / 100.0) * self.player.song_length
            self.current_time_var.set(utils.format_time(position))

    def update_progress(self):
        """Update progress bar and time display"""
        # We keep last_time/last_pos to interpolate rendering between pygame.get_pos updates
        if not hasattr(self, '_last_progress_time'):
            self._last_progress_time = None
            self._last_progress_pos = 0

        if self.player.is_playing and not self.player.paused and not self.dragging_progress:
            try:
                current_pos = self.player.get_current_position()
                now = time.time()
                if self._last_progress_time is None or now - self._last_progress_time > 0.25:
                    # update stored position
                    self._last_progress_time = now
                    self._last_progress_pos = current_pos
                else:
                    # interpolate forward smoothly
                    elapsed = now - self._last_progress_time
                    current_pos = self._last_progress_pos + elapsed
                    # do not exceed actual length
                    song_info = self.player.get_current_song_info()
                    if song_info and song_info['length'] > 0:
                        current_pos = min(current_pos, song_info['length'])
                song_info = self.player.get_current_song_info()

                if song_info and song_info['length'] > 0:
                    progress = (current_pos / song_info['length']) * 100
                    self.progress_var.set(progress)

                    # Update current time
                    self.current_time_var.set(utils.format_time(current_pos))
            except Exception as e:
                print(f"Progress update error: {e}")

        # Schedule next update
        self.root.after(200, self.update_progress)

    def check_music_events(self):
        """Check for music events like song end"""
        self.player.check_events()
        # Schedule next check
        self.root.after(100, self.check_music_events)

    def quit_app(self):
        """Quit application safely"""
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            # Save config (persist volume and last playlist)
            try:
                self.config['volume'] = float(self.player.volume)
                # Optionally save last playlist path list
                self.config['last_playlist'] = getattr(self.player, 'playlist', None)
                utils.save_config(CONFIG_FILE, self.config)
            except Exception:
                pass

            self.player.shutdown()
            self.root.quit()
            self.root.destroy()

    def run(self):
        """Start the application"""
        self.status_var.set("Ready - Add some music to get started!")
        print("🎵 Python Music Player is running...")
        print("Keyboard shortcuts:")
        print("  Space - Play/Pause")
        print("  → - Next song")
        print("  ← - Previous song")
        print("  Esc - Stop")
        print("  Ctrl+Q - Quit")

        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Application error: {e}")
        finally:
            self.player.shutdown()