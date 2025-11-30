#!/usr/bin/env python3
"""
Unit tests for UI components
"""
#!/usr/bin/env python3
"""
Unit tests for UI components
"""

import unittest
import tkinter as tk
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui import MusicPlayerApp
from utils import format_time, is_audio_file

class TestUtils(unittest.TestCase):
    
    def test_format_time(self):
        """Test time formatting function"""
        self.assertEqual(format_time(0), "0:00")
        self.assertEqual(format_time(65), "1:05")
        self.assertEqual(format_time(3605), "1:00:05")
        self.assertEqual(format_time(-10), "0:00")
    
    def test_is_audio_file(self):
        """Test audio file detection"""
        self.assertTrue(is_audio_file('test.mp3'))
        self.assertTrue(is_audio_file('test.MP3'))
        self.assertTrue(is_audio_file('test.wav'))
        self.assertTrue(is_audio_file('test.flac'))
        self.assertFalse(is_audio_file('test.txt'))
        self.assertFalse(is_audio_file('test'))

class TestUIComponents(unittest.TestCase):
    
    def setUp(self):
        """Set up UI tests"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
        
    def test_ui_creation(self):
        """Test UI creation without errors"""
        try:
            app = MusicPlayerApp()
            # Test that main components exist
            self.assertIsNotNone(app.player)
            self.assertIsNotNone(app.root)
        except Exception as e:
            self.fail(f"UI creation failed: {e}")
    
    def tearDown(self):
        """Clean up after UI tests"""
        if hasattr(self, 'app'):
            self.app.quit_app()
        self.root.destroy()

if __name__ == '__main__':
    unittest.main()
import unittest
import tkinter as tk
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui import MusicPlayerApp
from utils import format_time, is_audio_file

class TestUtils(unittest.TestCase):
    
    def test_format_time(self):
        """Test time formatting function"""
        self.assertEqual(format_time(0), "0:00")
        self.assertEqual(format_time(65), "1:05")
        self.assertEqual(format_time(3605), "1:00:05")
        self.assertEqual(format_time(-10), "0:00")
    
    def test_is_audio_file(self):
        """Test audio file detection"""
        self.assertTrue(is_audio_file('test.mp3'))
        self.assertTrue(is_audio_file('test.MP3'))
        self.assertTrue(is_audio_file('test.wav'))
        self.assertTrue(is_audio_file('test.flac'))
        self.assertFalse(is_audio_file('test.txt'))
        self.assertFalse(is_audio_file('test'))

class TestUIComponents(unittest.TestCase):
    
    def setUp(self):
        """Set up UI tests"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
        
    def test_ui_creation(self):
        """Test UI creation without errors"""
        try:
            app = MusicPlayerApp()
            # Test that main components exist
            self.assertIsNotNone(app.player)
            self.assertIsNotNone(app.root)
        except Exception as e:
            self.fail(f"UI creation failed: {e}")
    
    def tearDown(self):
        """Clean up after UI tests"""
        if hasattr(self, 'app'):
            self.app.quit_app()
        self.root.destroy()

if __name__ == '__main__':
    unittest.main()