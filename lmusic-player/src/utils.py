#!/usr/bin/env python3
"""
Utility functions for Python Music Player
"""

import os
import json
#!/usr/bin/env python3
"""
Utility functions for Python Music Player
"""

import os
import json
import logging
from typing import List, Dict, Any


def setup_logging(level=logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_file_extension(file_path: str) -> str:
    """Get file extension in lowercase"""
    return os.path.splitext(file_path)[1].lower()


def format_time(seconds: float) -> str:
    """Format seconds to MM:SS or HH:MM:SS if needed"""
    try:
        if seconds is None or seconds <= 0:
            return "0:00"

        seconds = int(seconds)
    except Exception:
        return "0:00"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    s = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{s:02d}"
    else:
        return f"{minutes}:{s:02d}"


def create_directory(path: str) -> bool:
    """Create directory if it doesn't exist"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Could not create directory {path}: {e}")
        return False


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    from config import DEFAULT_CONFIG
    default_config = DEFAULT_CONFIG.copy()

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                # Merge with default config
                for key, value in loaded_config.items():
                    if key in default_config:
                        default_config[key] = value
                logging.info(f"Configuration loaded from {config_path}")
    except Exception as e:
        logging.warning(f"Could not load config from {config_path}: {e}")

    return default_config


def save_config(config_path: str, config: Dict[str, Any]) -> bool:
    """Save configuration to JSON file"""
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        logging.info(f"Configuration saved to {config_path}")
        return True
    except Exception as e:
        logging.error(f"Could not save config to {config_path}: {e}")
        return False


def get_audio_files_in_directory(directory: str) -> List[str]:
    """Get list of audio files in directory"""
    audio_extensions = ('.mp3', '.wav', '.ogg', '.m4a', '.flac')
    audio_files = []

    try:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and file.lower().endswith(audio_extensions):
                audio_files.append(file_path)
    except Exception as e:
        logging.error(f"Error reading directory {directory}: {e}")

    return audio_files


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def is_audio_file(file_path: str) -> bool:
    """Check if file is a supported audio file"""
    audio_extensions = ('.mp3', '.wav', '.ogg', '.m4a', '.flac')
    return get_file_extension(file_path) in audio_extensions


def get_human_readable_time(seconds: int) -> str:
    """Get human readable time string"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"