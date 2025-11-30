#!/usr/bin/env python3
"""
Core music player functionality using PyGame
"""

import pygame
import os
import logging

# Import mutagen optionally; tests may run in environments without it
try:
    from mutagen import File
    from mutagen.flac import FLAC
    from mutagen.mp3 import MP3
    from mutagen.oggvorbis import OggVorbis
    from mutagen.mp4 import MP4
except Exception:
    File = None
    FLAC = None
    MP3 = None
    OggVorbis = None
    MP4 = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MusicPlayer:
    def __init__(self):
        """Initialize the music player"""
        # Initialize mixer lazily; tests may not have audio devices
        try:
            self.initialize_mixer()
        except Exception:
            logger.warning("Mixer initialization failed during tests; continuing without audio")

        # Player state
        self.playlist = []
        self.current_index = 0
        self.paused = False
        self.volume = 0.7
        self.current_position = 0
        self.song_length = 0
        self.is_playing = False

        # Callbacks for UI updates
        self.on_song_change = None
        self.on_playback_end = None
        # Mute support
        self.muted = False
        self._last_volume = self.volume

        logger.info("Music Player initialized")
        # If a playlist was restored externally, it can be loaded by UI

    def initialize_mixer(self):
        """Initialize PyGame mixer with error handling"""
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            logger.info("PyGame mixer initialized successfully")
        except pygame.error as e:
            logger.error(f"Could not initialize audio mixer: {e}")
            raise Exception(f"Audio system error: {e}")

    def add_files(self, file_paths):
        """Add multiple files to playlist"""
        added_count = 0
        audio_extensions = ('.mp3', '.wav', '.ogg', '.m4a', '.flac')

        for file_path in file_paths:
            if os.path.isfile(file_path) and file_path.lower().endswith(audio_extensions):
                self.playlist.append(file_path)
                added_count += 1
                logger.debug(f"Added to playlist: {os.path.basename(file_path)}")
            else:
                logger.warning(f"Skipped invalid file: {file_path}")

        logger.info(f"Added {added_count} files to playlist")
        return added_count

    def load_playlist(self, file_paths):
        """Replace current playlist with provided list, return count"""
        self.playlist = []
        added = self.add_files(file_paths)
        return added

    def add_folder(self, folder_path):
        """Add all audio files from folder to playlist"""
        if not os.path.isdir(folder_path):
            raise Exception(f"Folder not found: {folder_path}")

        audio_files = []
        audio_extensions = ('.mp3', '.wav', '.ogg', '.m4a', '.flac')

        try:
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path) and file.lower().endswith(audio_extensions):
                    audio_files.append(file_path)
        except PermissionError as e:
            raise Exception(f"Permission denied accessing folder: {e}")
        except Exception as e:
            raise Exception(f"Error reading folder: {e}")

        self.playlist.extend(audio_files)
        logger.info(f"Added {len(audio_files)} files from folder: {folder_path}")
        return len(audio_files)

    def play(self, index=None, fade_ms=0, start_pos=0.0):
        """Play song at specified index or current index
        fade_ms: fade-in time in milliseconds for the new track
        """
        if not self.playlist:
            logger.warning("No songs in playlist")
            return False

        if index is not None:
            if 0 <= index < len(self.playlist):
                self.current_index = index
            else:
                logger.error(f"Invalid playlist index: {index}")
                return False

        try:
            file_path = self.playlist[self.current_index]
            logger.info(f"Playing: {os.path.basename(file_path)}")

            # Stop any currently playing music
            try:
                # fade out any currently playing music slightly to avoid pops
                try:
                    pygame.mixer.music.fadeout(200)
                except Exception:
                    pass

                pygame.mixer.music.load(file_path)
                # Some formats/mixers support start position; if not, fallback
                try:
                    pygame.mixer.music.play(fade_ms=fade_ms, start=start_pos)
                except TypeError:
                    # Older pygame versions may not accept start on all formats
                    pygame.mixer.music.play(fade_ms=fade_ms)
            except Exception:
                # In case mixer isn't initialized (e.g., headless tests), skip actual playback
                logger.debug("Skipping real playback (mixer not available)")

            self.paused = False
            self.is_playing = True

            # Get song length
            self.song_length = self.get_song_length(file_path)

            # Set volume if mixer is available
            try:
                pygame.mixer.music.set_volume(self.volume)
            except Exception:
                pass

            # Notify UI about song change
            if self.on_song_change:
                self.on_song_change(self.get_current_song_info())

            # Set up end event detection if mixer exists
            try:
                pygame.mixer.music.set_endevent(pygame.USEREVENT)
            except Exception:
                pass

            return True

        except Exception as e:
            logger.error(f"Error playing file: {e}")
            raise

    def pause(self):
        """Pause current song"""
        if self.is_playing and not self.paused:
            try:
                pygame.mixer.music.pause()
            except Exception:
                pass
            self.paused = True
            logger.debug("Playback paused")

    def unpause(self):
        """Unpause current song"""
        if self.paused:
            try:
                pygame.mixer.music.unpause()
            except Exception:
                pass
            self.paused = False
            logger.debug("Playback resumed")

    def stop(self):
        """Stop playback"""
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self.paused = False
        self.is_playing = False
        self.current_position = 0
        logger.debug("Playback stopped")

    def next(self):
        """Play next song in playlist"""
        if not self.playlist:
            return False

        self.current_index = (self.current_index + 1) % len(self.playlist)
        logger.debug(f"Next song - index: {self.current_index}")
        return self.play(fade_ms=500)

    def previous(self):
        """Play previous song in playlist"""
        if not self.playlist:
            return False

        self.current_index = (self.current_index - 1) % len(self.playlist)
        logger.debug(f"Previous song - index: {self.current_index}")
        return self.play(fade_ms=500)

    def set_volume(self, volume):
        """Set volume level (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.volume)
        except Exception:
            pass
        logger.debug(f"Volume set to: {self.volume}")

    def toggle_mute(self):
        """Toggle mute/unmute; store and restore previous volume"""
        try:
            if not self.muted:
                self._last_volume = self.volume
                self.set_volume(0.0)
                self.muted = True
            else:
                self.set_volume(self._last_volume)
                self.muted = False
        except Exception:
            pass

    def get_current_position(self):
        """Get current playback position in seconds"""
        if not self.is_playing or self.paused:
            return self.current_position

        try:
            # PyGame returns position in milliseconds
            return pygame.mixer.music.get_pos() / 1000.0
        except Exception:
            return self.current_position

    def get_song_length(self, file_path):
        """Get song length in seconds using mutagen"""
        try:
            if File is None:
                return 0
            if file_path.lower().endswith('.mp3') and MP3 is not None:
                audio = MP3(file_path)
            elif file_path.lower().endswith('.flac') and FLAC is not None:
                audio = FLAC(file_path)
            elif file_path.lower().endswith('.ogg') and OggVorbis is not None:
                audio = OggVorbis(file_path)
            elif file_path.lower().endswith('.m4a') and MP4 is not None:
                audio = MP4(file_path)
            else:
                audio = File(file_path) if File is not None else None

            if audio is not None and hasattr(audio, 'info'):
                return int(getattr(audio.info, 'length', 0))
        except Exception as e:
            logger.warning(f"Could not get song length for {file_path}: {e}")

        return 0  # Unknown length

    def get_current_song_info(self):
        """Get info about currently playing song"""
        if not self.playlist or self.current_index >= len(self.playlist):
            return None

        file_path = self.playlist[self.current_index]
        file_name = os.path.basename(file_path)

        try:
            title = file_name
            artist = 'Unknown Artist'
            if File is not None:
                audio = None
                if file_path.lower().endswith('.mp3') and MP3 is not None:
                    audio = MP3(file_path)
                elif file_path.lower().endswith('.flac') and FLAC is not None:
                    audio = FLAC(file_path)
                else:
                    audio = File(file_path)

                if audio is not None:
                    # Many mutagen types expose tags differently; attempt common fields
                    tags = getattr(audio, 'tags', None)
                    if tags:
                        if 'title' in tags:
                            title = tags['title'][0]
                        if 'artist' in tags:
                            artist = tags['artist'][0]
        except Exception as e:
            logger.warning(f"Could not read metadata for {file_path}: {e}")
            title = file_name
            artist = 'Unknown Artist'

        return {
            'file_path': file_path,
            'file_name': file_name,
            'title': str(title),
            'artist': str(artist),
            'length': self.song_length,
            'position': self.get_current_position()
        }

    def clear_playlist(self):
        """Clear the playlist"""
        self.stop()
        self.playlist.clear()
        self.current_index = 0
        logger.info("Playlist cleared")

    def remove_from_playlist(self, index):
        """Remove song from playlist at specified index"""
        if 0 <= index < len(self.playlist):
            removed_file = self.playlist.pop(index)

            # Adjust current index if needed
            if index < self.current_index:
                self.current_index -= 1
            elif index == self.current_index:
                self.stop()
                if self.playlist:
                    self.current_index = min(self.current_index, len(self.playlist) - 1)
                else:
                    self.current_index = 0

            logger.info(f"Removed from playlist: {os.path.basename(removed_file)}")
            return True
        return False

    def check_events(self):
        """Check for music events (like song end)"""
        try:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:  # Song ended
                    logger.debug("Song ended event received")
                    if self.on_playback_end:
                        self.on_playback_end()
                    return True
        except Exception:
            pass
        return False

    def shutdown(self):
        """Cleanup resources"""
        self.stop()
        try:
            pygame.mixer.quit()
        except Exception:
            pass
        logger.info("Music player shutdown complete")