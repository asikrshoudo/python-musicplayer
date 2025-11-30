#!/usr/bin/env python3
"""
Unit tests for music player functionality
"""
#!/usr/bin/env python3
"""
Unit tests for music player functionality
"""

import unittest
import os
import tempfile
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from player import MusicPlayer

class TestMusicPlayer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.player = MusicPlayer()
        
    def test_initial_state(self):
        """Test initial state of music player"""
        self.assertEqual(len(self.player.playlist), 0)
        self.assertEqual(self.player.current_index, 0)
        self.assertEqual(self.player.volume, 0.7)
        self.assertFalse(self.player.paused)
        self.assertFalse(self.player.is_playing)
    
    def test_volume_range(self):
        """Test volume setting within valid range"""
        # Test normal volume
        self.player.set_volume(0.5)
        self.assertEqual(self.player.volume, 0.5)
        
        # Test lower bound
        self.player.set_volume(-0.5)
        self.assertEqual(self.player.volume, 0.0)
        
        # Test upper bound  
        self.player.set_volume(1.5)
        self.assertEqual(self.player.volume, 1.0)
    
    def test_playlist_management(self):
        """Test adding files to playlist"""
        # Create temporary test files
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f1, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f2:
            
            test_files = [f1.name, f2.name]
            
            try:
                # Test adding files
                count = self.player.add_files(test_files)
                self.assertEqual(count, 2)
                self.assertEqual(len(self.player.playlist), 2)
                
                # Test adding invalid file
                count = self.player.add_files(['nonexistent.mp3'])
                self.assertEqual(count, 0)
                self.assertEqual(len(self.player.playlist), 2)
                
            finally:
                # Cleanup
                for f in test_files:
                    if os.path.exists(f):
                        os.unlink(f)
    
    def test_clear_playlist(self):
        """Test clearing playlist"""
        # Add some dummy files to playlist
        self.player.playlist = ['test1.mp3', 'test2.mp3']
        self.player.current_index = 1
        
        self.player.clear_playlist()
        
        self.assertEqual(len(self.player.playlist), 0)
        self.assertEqual(self.player.current_index, 0)
        self.assertFalse(self.player.is_playing)
    
    def test_remove_from_playlist(self):
        """Test removing items from playlist"""
        self.player.playlist = ['song1.mp3', 'song2.mp3', 'song3.mp3']
        
        # Remove middle item
        result = self.player.remove_from_playlist(1)
        self.assertTrue(result)
        self.assertEqual(self.player.playlist, ['song1.mp3', 'song3.mp3'])
        
        # Remove first item
        self.player.current_index = 1
        self.player.remove_from_playlist(0)
        self.assertEqual(self.player.playlist, ['song3.mp3'])
        self.assertEqual(self.player.current_index, 0)  # Adjusted
    
    def tearDown(self):
        """Clean up after tests"""
        self.player.shutdown()

if __name__ == '__main__':
    unittest.main()
import unittest
import os
import tempfile
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from player import MusicPlayer

class TestMusicPlayer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.player = MusicPlayer()
        
    def test_initial_state(self):
        """Test initial state of music player"""
        self.assertEqual(len(self.player.playlist), 0)
        self.assertEqual(self.player.current_index, 0)
        self.assertEqual(self.player.volume, 0.7)
        self.assertFalse(self.player.paused)
        self.assertFalse(self.player.is_playing)
    
    def test_volume_range(self):
        """Test volume setting within valid range"""
        # Test normal volume
        self.player.set_volume(0.5)
        self.assertEqual(self.player.volume, 0.5)
        
        # Test lower bound
        self.player.set_volume(-0.5)
        self.assertEqual(self.player.volume, 0.0)
        
        # Test upper bound  
        self.player.set_volume(1.5)
        self.assertEqual(self.player.volume, 1.0)
    
    def test_playlist_management(self):
        """Test adding files to playlist"""
        # Create temporary test files
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f1, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f2:
            
            test_files = [f1.name, f2.name]
            
            try:
                # Test adding files
                count = self.player.add_files(test_files)
                self.assertEqual(count, 2)
                self.assertEqual(len(self.player.playlist), 2)
                
                # Test adding invalid file
                count = self.player.add_files(['nonexistent.mp3'])
                self.assertEqual(count, 0)
                self.assertEqual(len(self.player.playlist), 2)
                
            finally:
                # Cleanup
                for f in test_files:
                    if os.path.exists(f):
                        os.unlink(f)
    
    def test_clear_playlist(self):
        """Test clearing playlist"""
        # Add some dummy files to playlist
        self.player.playlist = ['test1.mp3', 'test2.mp3']
        self.player.current_index = 1
        
        self.player.clear_playlist()
        
        self.assertEqual(len(self.player.playlist), 0)
        self.assertEqual(self.player.current_index, 0)
        self.assertFalse(self.player.is_playing)
    
    def test_remove_from_playlist(self):
        """Test removing items from playlist"""
        self.player.playlist = ['song1.mp3', 'song2.mp3', 'song3.mp3']
        
        # Remove middle item
        result = self.player.remove_from_playlist(1)
        self.assertTrue(result)
        self.assertEqual(self.player.playlist, ['song1.mp3', 'song3.mp3'])
        
        # Remove first item
        self.player.current_index = 1
        self.player.remove_from_playlist(0)
        self.assertEqual(self.player.playlist, ['song3.mp3'])
        self.assertEqual(self.player.current_index, 0)  # Adjusted
    
    def tearDown(self):
        """Clean up after tests"""
        self.player.shutdown()

if __name__ == '__main__':
    unittest.main()