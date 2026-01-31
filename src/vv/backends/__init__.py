"""Transcription backends with automatic platform detection."""

from __future__ import annotations

import platform
import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from numpy.typing import NDArray
    import numpy as np


class TranscriptionResult:
    """Result from transcription."""

    def __init__(
        self,
        text: str,
        segments: list[dict] | None = None,
        language: str | None = None,
    ):
        self.text = text
        self.segments = segments or []
        self.language = language


class TranscriptionBackend(ABC):
    """Abstract base class for transcription backends."""

    @abstractmethod
    def load_model(self, model_size: str) -> None:
        """Load a Whisper model of the given size."""
        pass

    @abstractmethod
    def transcribe(
        self,
        audio: NDArray[np.float32],
        language: str | None = None,
        word_timestamps: bool = False,
    ) -> TranscriptionResult:
        """Transcribe audio data.

        Args:
            audio: Audio data as float32 numpy array
            language: Language code (e.g., 'en') or None for auto-detect
            word_timestamps: Whether to include word-level timestamps

        Returns:
            TranscriptionResult with text and optional segments
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the backend name for display."""
        pass


def get_backend() -> TranscriptionBackend:
    """Select optimal transcription backend for current platform.

    On Apple Silicon, prefers mlx-whisper if available.
    Falls back to faster-whisper on all platforms.

    Returns:
        TranscriptionBackend instance
    """
    # Apple Silicon: prefer mlx-whisper (10x faster, much smaller)
    if sys.platform == "darwin" and platform.machine() == "arm64":
        try:
            from vv.backends.mlx import MLXBackend

            return MLXBackend()
        except ImportError:
            pass  # Fall through to cross-platform backend

    # Cross-platform: use faster-whisper
    from vv.backends.faster import FasterWhisperBackend

    return FasterWhisperBackend()
