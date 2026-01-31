"""Tests for CLI functions."""

import pytest

from vv import __version__
from vv.backends import TranscriptionResult
from vv.cli import create_parser, format_output, format_timestamp


class TestFormatTimestamp:
    """Tests for format_timestamp function."""

    def test_zero_seconds(self):
        assert format_timestamp(0) == "0:00"

    def test_under_one_minute(self):
        assert format_timestamp(45) == "0:45"

    def test_exactly_one_minute(self):
        assert format_timestamp(60) == "1:00"

    def test_over_one_minute(self):
        assert format_timestamp(90) == "1:30"

    def test_multiple_minutes(self):
        assert format_timestamp(125) == "2:05"

    def test_rounds_down_fractional_seconds(self):
        assert format_timestamp(45.9) == "0:45"


class TestFormatOutput:
    """Tests for format_output function."""

    def test_quiet_mode_returns_only_text(self):
        result = TranscriptionResult(text="Hello world")
        output = format_output(result, duration=5.0, quiet=True)
        assert output == "Hello world"

    def test_quiet_mode_with_timestamps(self):
        result = TranscriptionResult(
            text="Hello world",
            segments=[
                {"start": 0.0, "end": 2.5, "text": "Hello"},
                {"start": 2.5, "end": 5.0, "text": "world"},
            ],
        )
        output = format_output(result, duration=5.0, show_timestamps=True, quiet=True)
        assert "[0:00-0:02] Hello" in output
        assert "[0:02-0:05] world" in output

    def test_full_output_includes_header(self):
        result = TranscriptionResult(text="Test", language="en")
        output = format_output(result, duration=3.0, quiet=False)
        assert "TRANSCRIPTION" in output
        assert "Test" in output
        assert "Duration: 3.00s" in output
        assert "Language: en" in output


class TestCreateParser:
    """Tests for argument parser."""

    def test_parser_defaults(self):
        parser = create_parser()
        args = parser.parse_args([])
        assert args.model == "base"
        assert args.language is None
        assert args.output is None
        assert args.copy is False
        assert args.once is False
        assert args.quiet is False

    def test_model_flag(self):
        parser = create_parser()
        args = parser.parse_args(["-m", "large"])
        assert args.model == "large"

    def test_language_flag(self):
        parser = create_parser()
        args = parser.parse_args(["-l", "en"])
        assert args.language == "en"

    def test_combined_flags(self):
        parser = create_parser()
        args = parser.parse_args(["-1", "-c", "-q"])
        assert args.once is True
        assert args.copy is True
        assert args.quiet is True


class TestTranscriptionResult:
    """Tests for TranscriptionResult dataclass."""

    def test_basic_creation(self):
        result = TranscriptionResult(text="Hello")
        assert result.text == "Hello"
        assert result.segments == []
        assert result.language is None

    def test_with_all_fields(self):
        segments = [{"start": 0, "end": 1, "text": "Hi"}]
        result = TranscriptionResult(text="Hi", segments=segments, language="en")
        assert result.text == "Hi"
        assert result.segments == segments
        assert result.language == "en"


class TestVersion:
    """Tests for version."""

    def test_version_is_string(self):
        assert isinstance(__version__, str)

    def test_version_format(self):
        # Should be semver-ish (x.y.z)
        parts = __version__.split(".")
        assert len(parts) >= 2
