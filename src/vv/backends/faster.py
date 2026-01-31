"""Faster-whisper backend for cross-platform transcription."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from vv.backends import TranscriptionBackend, TranscriptionResult

if TYPE_CHECKING:
    import numpy as np
    from numpy.typing import NDArray


class FasterWhisperBackend(TranscriptionBackend):
    """Transcription backend using faster-whisper (CTranslate2)."""

    def __init__(self) -> None:
        self._model = None

    @property
    def name(self) -> str:
        return "faster-whisper"

    def load_model(self, model_size: str) -> None:
        """Load a faster-whisper model.

        Args:
            model_size: One of tiny, base, small, medium, large-v2, large-v3
        """
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            print("Error: faster-whisper is not installed.", file=sys.stderr)
            print("Install with: pip install faster-whisper", file=sys.stderr)
            sys.exit(4)

        try:
            # Use int8 quantization for smaller memory footprint
            # auto device selection (cuda if available, else cpu)
            self._model = WhisperModel(model_size, device="auto", compute_type="int8")
        except Exception as e:
            print(f"Error loading model '{model_size}': {e}", file=sys.stderr)
            sys.exit(4)

    def transcribe(
        self,
        audio: NDArray[np.float32],
        language: str | None = None,
        word_timestamps: bool = False,
    ) -> TranscriptionResult:
        """Transcribe audio using faster-whisper.

        Args:
            audio: Audio data as float32 numpy array (mono, 16kHz)
            language: Language code or None for auto-detect
            word_timestamps: Whether to include word-level timestamps

        Returns:
            TranscriptionResult with text and segments
        """
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Flatten audio if needed
        if audio.ndim > 1:
            audio = audio.flatten()

        try:
            segments_iter, info = self._model.transcribe(
                audio,
                language=language,
                word_timestamps=word_timestamps,
                # Verbatim transcription settings
                suppress_tokens=[],  # Don't suppress any tokens
                condition_on_previous_text=True,
            )

            # Collect segments
            segments = []
            text_parts = []
            for segment in segments_iter:
                text_parts.append(segment.text)
                seg_dict = {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                }
                if word_timestamps and segment.words:
                    seg_dict["words"] = [
                        {"start": w.start, "end": w.end, "word": w.word}
                        for w in segment.words
                    ]
                segments.append(seg_dict)

            text = "".join(text_parts).strip()

            return TranscriptionResult(
                text=text,
                segments=segments,
                language=info.language,
            )

        except Exception as e:
            print(f"Error during transcription: {e}", file=sys.stderr)
            sys.exit(5)
