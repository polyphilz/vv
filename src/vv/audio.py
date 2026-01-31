"""Audio recording functionality."""

from __future__ import annotations

import sys
import threading
from typing import TYPE_CHECKING

import numpy as np
import sounddevice as sd

if TYPE_CHECKING:
    from numpy.typing import NDArray


def list_devices() -> str:
    """Return a formatted string of available audio input devices."""
    devices = sd.query_devices()
    lines = ["Available audio input devices:", ""]

    for i, device in enumerate(devices):
        if device["max_input_channels"] > 0:
            default_marker = " (default)" if device == sd.query_devices(kind="input") else ""
            lines.append(f"  [{i}] {device['name']}{default_marker}")

    return "\n".join(lines)


def record_audio(
    sample_rate: int = 16000,
    quiet: bool = False,
) -> tuple[NDArray[np.float32], float, int]:
    """Record audio from the default microphone until Enter is pressed.

    Args:
        sample_rate: Audio sample rate in Hz (default: 16000 for Whisper)
        quiet: If True, suppress recording prompts

    Returns:
        Tuple of (audio_data, duration_seconds, sample_rate)

    Raises:
        SystemExit: If microphone cannot be accessed
    """
    recording: list[NDArray[np.float32]] = []
    stop_event = threading.Event()

    def callback(
        indata: NDArray[np.float32],
        frames: int,
        time_info: dict,
        status: sd.CallbackFlags,
    ) -> None:
        if status:
            print(f"Warning: {status}", file=sys.stderr)
        if not stop_event.is_set():
            recording.append(indata.copy())

    try:
        stream = sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype=np.float32,
            callback=callback,
        )
    except sd.PortAudioError as e:
        print(f"Error: Could not access microphone: {e}", file=sys.stderr)
        print("On macOS, check System Preferences > Security & Privacy > Microphone", file=sys.stderr)
        sys.exit(3)

    if not quiet:
        print("\nRecording... Press Enter to stop.\n")

    try:
        with stream:
            input()
    except EOFError:
        pass  # stdin closed, stop recording
    finally:
        stop_event.set()

    if not recording:
        return np.array([], dtype=np.float32), 0.0, sample_rate

    audio_data = np.concatenate(recording, axis=0)
    # Clip to prevent overflow when converting to int16 later
    audio_data = np.clip(audio_data, -1.0, 1.0)
    duration = len(audio_data) / sample_rate

    return audio_data, duration, sample_rate
