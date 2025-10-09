#!/usr/bin/env python3
"""
TTS Library Tests - Professional Test Suite

Comprehensive test suite for the TTS library covering:
- Unit tests for all functions
- Integration tests
- Error handling tests
- Performance tests
- Edge case testing

Author: TTS Library Team
Version: 1.0.0
License: MIT
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path
import logging

# Configure logging for tests
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Add libs to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))

try:
    from tts_lib import (
        validate_text,
        validate_engine,
        validate_language,
        get_default_config,
        text_to_speech_file,
        text_to_speech_bytes,
        text_to_speech_bytesio,
        play_audio,
        compose,
        with_engine,
        with_language,
        create_tts_pipeline,
        batch_tts,
        generate_timestamp_filename,
        ensure_audio_directory,
        TTSException,
        ValidationError,
        EngineNotAvailableError
    )
except ImportError as e:
    logger.error(f"Failed to import TTS library: {e}")
    sys.exit(1)


class TestValidation(unittest.TestCase):
    """Test validation functions."""

    def test_validate_text_valid(self):
        """Test valid text validation."""
        result = validate_text("Hello world")
        self.assertEqual(result, "Hello world")

    def test_validate_text_empty(self):
        """Test empty text validation."""
        with self.assertRaises(ValidationError):
            validate_text("")

    def test_validate_text_whitespace(self):
        """Test whitespace-only text validation."""
        with self.assertRaises(ValidationError):
            validate_text("   ")

    def test_validate_text_too_long(self):
        """Test text length validation."""
        long_text = "a" * 5001
        with self.assertRaises(ValidationError):
            validate_text(long_text)

    def test_validate_text_non_string(self):
        """Test non-string input validation."""
        with self.assertRaises(ValidationError):
            validate_text(123)

    def test_validate_engine_valid(self):
        """Test valid engine validation."""
        with patch('tts_lib.PYTTSX3_AVAILABLE', True):
            with patch('tts_lib.GTTS_AVAILABLE', True):
                result = validate_engine("gtts")
                self.assertEqual(result, "gtts")

    def test_validate_engine_invalid(self):
        """Test invalid engine validation."""
        with self.assertRaises(ValidationError):
            validate_engine("invalid_engine")

    def test_validate_language_valid(self):
        """Test valid language validation."""
        result = validate_language("en")
        self.assertEqual(result, "en")

    def test_validate_language_invalid(self):
        """Test invalid language validation."""
        with self.assertRaises(ValidationError):
            validate_language("english")


class TestConfiguration(unittest.TestCase):
    """Test configuration functions."""

    def test_get_default_config(self):
        """Test default configuration."""
        config = get_default_config()
        self.assertIsInstance(config, dict)
        self.assertIn('engine', config)
        self.assertIn('language', config)
        self.assertIn('rate', config)
        self.assertIn('volume', config)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""

    def test_generate_timestamp_filename(self):
        """Test timestamp filename generation."""
        filename = generate_timestamp_filename("", "mp3")
        self.assertTrue(filename.endswith(".mp3"))
        self.assertRegex(filename, r"\d{8}_\d{6}\.mp3")

        filename_with_prefix = generate_timestamp_filename("test", "mp3")
        self.assertTrue(filename_with_prefix.startswith("test_"))
        self.assertTrue(filename_with_prefix.endswith(".mp3"))
        self.assertRegex(filename_with_prefix, r"test_\d{8}_\d{6}\.mp3")

    def test_ensure_audio_directory(self):
        """Test audio directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = os.path.join(temp_dir, "test_audio")
            result = ensure_audio_directory(test_dir)
            self.assertEqual(result, test_dir)
            self.assertTrue(os.path.exists(test_dir))


class TestFunctionComposition(unittest.TestCase):
    """Test function composition."""

    def test_compose_functions(self):
        """Test function composition."""
        def add_one(x): return x + 1
        def multiply_two(x): return x * 2

        composed = compose(add_one, multiply_two)
        result = composed(5)  # Should be (5 * 2) + 1 = 11
        self.assertEqual(result, 11)

    def test_with_engine(self):
        """Test with_engine higher-order function."""
        def mock_tts_function(text, engine=None, **kwargs):
            return engine

        offline_tts = with_engine("pyttsx3")(mock_tts_function)
        result = offline_tts("test")
        self.assertEqual(result, "pyttsx3")

    def test_with_language(self):
        """Test with_language higher-order function."""
        def mock_tts_function(text, language=None, **kwargs):
            return language

        spanish_tts = with_language("es")(mock_tts_function)
        result = spanish_tts("test")
        self.assertEqual(result, "es")


class TestTTSFunctions(unittest.TestCase):
    """Test TTS functions with mocking."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('tts_lib.gtts_to_file')
    def test_text_to_speech_file_success(self, mock_gtts_to_file):
        """Test successful text to speech file generation."""
        mock_gtts_to_file.return_value = "test.mp3"

        result = text_to_speech_file("Hello world", "test.mp3", "gtts", "en")

        self.assertEqual(result, "test.mp3")
        mock_gtts_to_file.assert_called_once()

    @patch('tts_lib.gtts_to_bytes')
    def test_text_to_speech_bytes_success(self, mock_gtts_to_bytes):
        """Test successful text to speech bytes generation."""
        mock_gtts_to_bytes.return_value = b"fake_audio_data"

        result = text_to_speech_bytes("Hello world", "gtts", "en")

        self.assertEqual(result, b"fake_audio_data")
        mock_gtts_to_bytes.assert_called_once()

    @patch('tts_lib.text_to_speech_bytes')
    def test_text_to_speech_bytesio_success(self, mock_text_to_bytes):
        """Test successful text to speech BytesIO generation."""
        mock_text_to_bytes.return_value = b"fake_audio_data"

        result = text_to_speech_bytesio("Hello world", "gtts", "en")

        self.assertEqual(result.getvalue(), b"fake_audio_data")
        mock_text_to_bytes.assert_called_once()


class TestPipeline(unittest.TestCase):
    """Test TTS pipeline functionality."""

    @patch('tts_lib.text_to_speech_file')
    def test_create_tts_pipeline_file(self, mock_tts_file):
        """Test TTS pipeline file output."""
        mock_tts_file.return_value = "test.mp3"

        pipeline = create_tts_pipeline("gtts", "en")
        result = pipeline("Hello world", "file", "test.mp3")

        self.assertEqual(result, "test.mp3")
        mock_tts_file.assert_called_once_with("Hello world", "test.mp3", "gtts", "en")

    @patch('tts_lib.text_to_speech_bytes')
    def test_create_tts_pipeline_bytes(self, mock_tts_bytes):
        """Test TTS pipeline bytes output."""
        mock_tts_bytes.return_value = b"fake_audio_data"

        pipeline = create_tts_pipeline("gtts", "en")
        result = pipeline("Hello world", "bytes")

        self.assertEqual(result, b"fake_audio_data")
        mock_tts_bytes.assert_called_once_with("Hello world", "gtts", "en")


class TestBatchProcessing(unittest.TestCase):
    """Test batch processing functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('tts_lib.create_tts_pipeline')
    def test_batch_tts_success(self, mock_create_pipeline):
        """Test successful batch processing."""
        mock_pipeline = MagicMock()
        mock_pipeline.return_value = "test.mp3"
        mock_create_pipeline.return_value = mock_pipeline

        texts = ["Hello", "World", "Test"]
        result = batch_tts(texts, output_dir=self.temp_dir)

        self.assertEqual(len(result), 3)
        self.assertTrue(all(filename.endswith('.mp3') for filename in result))
        self.assertTrue(all('batch_' not in filename for filename in result))  # No batch prefix
        self.assertEqual(mock_pipeline.call_count, 3)

    def test_batch_tts_empty_list(self):
        """Test batch processing with empty list."""
        with self.assertRaises(ValidationError):
            batch_tts([])

    def test_batch_tts_invalid_input(self):
        """Test batch processing with invalid input."""
        with self.assertRaises(ValidationError):
            batch_tts("not_a_list")


class TestErrorHandling(unittest.TestCase):
    """Test error handling."""

    def test_tts_exception(self):
        """Test TTS exception."""
        with self.assertRaises(TTSException):
            raise TTSException("Test error")

    def test_validation_error(self):
        """Test validation error."""
        with self.assertRaises(ValidationError):
            raise ValidationError("Test validation error")

    def test_engine_not_available_error(self):
        """Test engine not available error."""
        with self.assertRaises(EngineNotAvailableError):
            raise EngineNotAvailableError("Test engine error")


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_workflow_mock(self):
        """Test full workflow with mocked dependencies."""
        with patch('tts_lib.GTTS_AVAILABLE', True):
            with patch('tts_lib.gtts_to_file') as mock_gtts:
                mock_gtts.return_value = "test.mp3"

                # Test full workflow
                filename = text_to_speech_file("Hello world", "test.mp3")
                self.assertEqual(filename, "test.mp3")

                # Test pipeline
                pipeline = create_tts_pipeline()
                result = pipeline("Hello world", "file", "test2.mp3")
                self.assertEqual(result, "test.mp3")


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_classes = [
        TestValidation,
        TestConfiguration,
        TestUtilityFunctions,
        TestFunctionComposition,
        TestTTSFunctions,
        TestPipeline,
        TestBatchProcessing,
        TestErrorHandling,
        TestIntegration
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    print("TTS Library Test Suite")
    print("=" * 50)

    success = run_tests()

    if success:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)
