"""MLX-whisper backend for Apple Silicon optimization."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from vv.backends import TranscriptionBackend, TranscriptionResult

if TYPE_CHECKING:
    import numpy as np
    from numpy.typing import NDArray


class MLXBackend(TranscriptionBackend):
    """Transcription backend using mlx-whisper for Apple Silicon."""

    def __init__(self) -> None:
        # Import check - will raise ImportError if not available
        try:
            import mlx_whisper  # noqa: F401
        except ImportError:
            raise ImportError("mlx-whisper is not installed")
        self._model_path: str | None = None

    @property
    def name(self) -> str:
        return "mlx-whisper"

    def load_model(self, model_size: str) -> None:
        """Load an MLX whisper model.

        Args:
            model_size: One of tiny, base, small, medium, large-v2, large-v3
        """
        # mlx-whisper uses HuggingFace model paths
        model_map = {
            "tiny": "mlx-community/whisper-tiny-mlx",
            "base": "mlx-community/whisper-base-mlx",
            "small": "mlx-community/whisper-small-mlx",
            "medium": "mlx-community/whisper-medium-mlx",
            "large": "mlx-community/whisper-large-v3-mlx",
            "large-v2": "mlx-community/whisper-large-v2-mlx",
            "large-v3": "mlx-community/whisper-large-v3-mlx",
        }

        if model_size not in model_map:
            print(f"Error: Unknown model size '{model_size}'", file=sys.stderr)
            print(f"Available: {', '.join(model_map.keys())}", file=sys.stderr)
            sys.exit(4)

        self._model_path = model_map[model_size]
        # Model will be downloaded on first transcribe if not cached

    def transcribe(
        self,
        audio: NDArray[np.float32],
        language: str | None = None,
        word_timestamps: bool = False,
    ) -> TranscriptionResult:
        """Transcribe audio using mlx-whisper.

        Args:
            audio: Audio data as float32 numpy array (mono, 16kHz)
            language: Language code or None for auto-detect
            word_timestamps: Whether to include word-level timestamps

        Returns:
            TranscriptionResult with text and segments
        """
        if self._model_path is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        import mlx_whisper

        # Flatten audio if needed
        if audio.ndim > 1:
            audio = audio.flatten()

        try:
            result = mlx_whisper.transcribe(
                audio,
                path_or_hf_repo=self._model_path,
                language=language,
                word_timestamps=word_timestamps,
            )

            # Parse result
            text = result.get("text", "").strip()
            segments = []

            for seg in result.get("segments", []):
                seg_dict = {
                    "start": seg.get("start", 0),
                    "end": seg.get("end", 0),
                    "text": seg.get("text", "").strip(),
                }
                if word_timestamps and "words" in seg:
                    seg_dict["words"] = [
                        {"start": w["start"], "end": w["end"], "word": w["word"]}
                        for w in seg["words"]
                    ]
                segments.append(seg_dict)

            return TranscriptionResult(
                text=text,
                segments=segments,
                language=result.get("language"),
            )

        except Exception as e:
            print(f"Error during transcription: {e}", file=sys.stderr)
            sys.exit(5)
