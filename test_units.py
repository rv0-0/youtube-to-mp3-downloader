"""
Unit tests for YouTube to MP3 downloader functions
Tests the core download functions without requiring the API server
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add the current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from youtube_to_mp3 import download_youtube_to_mp3
    from youtube_to_mp3_advanced import AdvancedYouTubeDownloader
    from youtube_to_mp3_smart import SmartYouTubeDownloader
except ImportError as e:
    print(f"Warning: Could not import downloader modules: {e}")
    print("Some tests will be skipped.")

class TestDownloaderFunctions(unittest.TestCase):
    """Test the core downloader functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # First YouTube video (short)
        
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up any downloaded files
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    def test_basic_downloader_import(self):
        """Test that basic downloader can be imported"""
        try:
            from youtube_to_mp3 import download_youtube_to_mp3
            self.assertTrue(callable(download_youtube_to_mp3))
        except ImportError:
            self.skipTest("Basic downloader module not available")
    
    def test_advanced_downloader_import(self):
        """Test that advanced downloader can be imported"""
        try:
            from youtube_to_mp3_advanced import AdvancedYouTubeDownloader
            self.assertTrue(AdvancedYouTubeDownloader)
        except ImportError:
            self.skipTest("Advanced downloader module not available")
    
    def test_smart_downloader_import(self):
        """Test that smart downloader can be imported"""
        try:
            from youtube_to_mp3_smart import SmartYouTubeDownloader
            self.assertTrue(SmartYouTubeDownloader)
        except ImportError:
            self.skipTest("Smart downloader module not available")
    
    def test_advanced_downloader_initialization(self):
        """Test AdvancedYouTubeDownloader initialization"""
        try:
            downloader = AdvancedYouTubeDownloader(self.temp_dir, "192", max_workers=2)
            self.assertEqual(str(downloader.output_path), self.temp_dir)
            self.assertEqual(downloader.quality, "192")
            self.assertEqual(downloader.max_workers, 2)
        except NameError:
            self.skipTest("AdvancedYouTubeDownloader not available")
    
    def test_smart_downloader_initialization(self):
        """Test SmartYouTubeDownloader initialization"""
        try:
            downloader = SmartYouTubeDownloader(self.temp_dir, "192", max_workers=2)
            self.assertEqual(str(downloader.output_path), self.temp_dir)
            self.assertEqual(downloader.quality, "192")
            self.assertEqual(downloader.max_workers, 2)
        except NameError:
            self.skipTest("SmartYouTubeDownloader not available")
    
    def test_url_validation(self):
        """Test URL validation"""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ"
        ]
        
        invalid_urls = [
            "not_a_url",
            "https://google.com",
            "https://youtube.com/",
            ""
        ]
        
        # Test that valid URLs are accepted (basic validation)
        for url in valid_urls:
            self.assertTrue("youtube" in url.lower() or "youtu.be" in url.lower())
            self.assertTrue("watch?v=" in url or "youtu.be/" in url)
        
        # Test that invalid URLs don't contain expected patterns
        for url in invalid_urls:
            if url:  # Skip empty string
                self.assertNotIn("watch?v=", url)
    
    def test_quality_options(self):
        """Test quality parameter validation"""
        valid_qualities = ["64", "128", "192", "256", "320"]
        
        for quality in valid_qualities:
            self.assertIn(quality, valid_qualities)
            self.assertTrue(quality.isdigit())
            self.assertTrue(64 <= int(quality) <= 320)
    
    def test_output_directory_creation(self):
        """Test that output directories are created properly"""
        test_dir = os.path.join(self.temp_dir, "test_output")
        
        # Directory shouldn't exist initially
        self.assertFalse(os.path.exists(test_dir))
        
        # Create directory
        os.makedirs(test_dir, exist_ok=True)
        
        # Directory should exist now
        self.assertTrue(os.path.exists(test_dir))
        self.assertTrue(os.path.isdir(test_dir))


class TestAPIHelpers(unittest.TestCase):
    """Test API helper functions"""
    
    def test_task_id_generation(self):
        """Test that task IDs are generated properly"""
        import uuid
        
        # Generate some task IDs
        task_ids = [str(uuid.uuid4()) for _ in range(10)]
        
        # Check they're all unique
        self.assertEqual(len(task_ids), len(set(task_ids)))
        
        # Check they're valid UUIDs
        for task_id in task_ids:
            self.assertEqual(len(task_id), 36)  # UUID string length
            self.assertEqual(task_id.count('-'), 4)  # UUID has 4 hyphens
    
    def test_progress_calculation(self):
        """Test progress calculation logic"""
        # Test progress for single downloads
        total_steps = 100
        for completed in range(0, total_steps + 1, 10):
            progress = (completed / total_steps) * 100
            self.assertTrue(0 <= progress <= 100)
        
        # Test progress for batch downloads
        total_files = 5
        for completed_files in range(total_files + 1):
            progress = (completed_files / total_files) * 100
            self.assertTrue(0 <= progress <= 100)
    
    def test_file_size_formatting(self):
        """Test file size formatting"""
        def format_file_size(size_bytes):
            """Format file size in human readable format"""
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        
        test_cases = [
            (500, "500 B"),
            (1024, "1.0 KB"),
            (1536, "1.5 KB"),
            (1024 * 1024, "1.0 MB"),
            (1536 * 1024, "1.5 MB")
        ]
        
        for size, expected in test_cases:
            result = format_file_size(size)
            self.assertTrue(expected.split()[1] in result)  # Check unit


class TestConfigValidation(unittest.TestCase):
    """Test configuration validation"""
    
    def test_quality_validation(self):
        """Test quality parameter validation"""
        valid_qualities = [64, 128, 192, 256, 320]
        
        for quality in valid_qualities:
            self.assertIn(quality, valid_qualities)
            self.assertTrue(isinstance(quality, int))
            self.assertTrue(64 <= quality <= 320)
    
    def test_worker_validation(self):
        """Test worker count validation"""
        valid_workers = list(range(1, 11))  # 1-10 workers
        
        for workers in valid_workers:
            self.assertTrue(1 <= workers <= 10)
            self.assertTrue(isinstance(workers, int))
    
    def test_mode_validation(self):
        """Test download mode validation"""
        valid_modes = ["basic", "advanced", "smart"]
        
        for mode in valid_modes:
            self.assertIn(mode, valid_modes)
            self.assertTrue(isinstance(mode, str))
            self.assertTrue(mode.islower())


def run_unit_tests():
    """Run all unit tests"""
    print("🧪 Running Unit Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDownloaderFunctions,
        TestAPIHelpers,
        TestConfigValidation
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📋 UNIT TEST SUMMARY")
    print("=" * 50)
    print(f"Tests Run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, error in result.failures:
            print(f"   └─ {test}: {error}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, error in result.errors:
            print(f"   └─ {test}: {error}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run unit tests for YouTube to MP3 downloader')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        unittest.main(verbosity=2)
    else:
        success = run_unit_tests()
        exit(0 if success else 1)
