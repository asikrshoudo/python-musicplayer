"""
Configuration settings for the music player
"""
#!/usr/bin/env python3
"""
Configuration constants for Python Music Player
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
ICONS_DIR = os.path.join(ASSETS_DIR, 'icons')

# Default config file path
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')

# Application identity
APP_NAME = 'lmusic-player'
# Default visual theme (kept simple)
DEFAULT_THEME = 'dark'
DEFAULT_CONFIG = {
    'volume': 0.7,
    'repeat': False,
    'shuffle': False,
    'last_playlist': None,
    'last_index': 0,
    'resume_on_start': False,
    'theme': DEFAULT_THEME,
}
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
PLAYLISTS_DIR = os.path.join(BASE_DIR, 'playlists')
ICONS_DIR = os.path.join(ASSETS_DIR, 'icons')

# Supported audio formats
SUPPORTED_FORMATS = {
    '.mp3': 'MP3 Audio',
    '.wav': 'WAV Audio',
    '.ogg': 'OGG Audio',
    '.flac': 'FLAC Audio',
    '.m4a': 'MPEG-4 Audio'
}

# Default settings
DEFAULT_SETTINGS = {
    'volume': 0.7,
    'repeat': False,
    'shuffle': False,
    'last_playlist': None,
    'window_size': [600, 500]
}

# Create necessary directories
for directory in [ASSETS_DIR, PLAYLISTS_DIR, ICONS_DIR]:
    os.makedirs(directory, exist_ok=True)