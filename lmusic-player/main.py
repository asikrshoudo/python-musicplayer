#!/usr/bin/env python3
"""
Main entry point for Python Music Player
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ui import MusicPlayerApp
try:
    from modern_ui import ModernMusicPlayerApp
except Exception:
    ModernMusicPlayerApp = None

def main():
    """Main function to start the music player"""
    try:
        # prefer modern UI if available
        if ModernMusicPlayerApp:
            app = ModernMusicPlayerApp()
            app.run()
        else:
            # fallback to classic UI
            app = MusicPlayerApp()
            app.run()
    except KeyboardInterrupt:
        print("\nGoodbye! 👋")
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()