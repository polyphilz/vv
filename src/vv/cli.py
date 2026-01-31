"""Command-line interface for vv."""

from __future__ import annotations

import argparse
import sys

from vv import __version__
from vv.audio import list_devices, record_audio
from vv.backends import get_backend


def format_timestamp(seconds: float) -> str:
    """Format seconds as MM:SS."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def format_output(
    result,
    duration: float,
    show_timestamps: bool = False,
    quiet: bool = False,
) -> str:
    """Format transcription result for output.

    Args:
        result: TranscriptionResult from backend
        duration: Recording duration in seconds
        show_timestamps: Whether to include timestamps
        quiet: If True, return only the text

    Returns:
        Formatted output string
    """
    if quiet:
        if show_timestamps and result.segments:
            lines = []
            for seg in result.segments:
                start = format_timestamp(seg["start"])
                end = format_timestamp(seg["end"])
                lines.append(f"[{start}-{end}] {seg['text']}")
            return "\n".join(lines)
        return result.text

    # Full output with decoration
    lines = [
        "",
        "=" * 50,
        "  TRANSCRIPTION",
        "=" * 50,
        "",
    ]

    if show_timestamps and result.segments:
        for seg in result.segments:
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            lines.append(f"[{start}-{end}] {seg['text']}")
    else:
        lines.append(result.text)

    lines.extend([
        "",
        f"Duration: {duration:.2f}s | Language: {result.language or 'unknown'}",
        "=" * 50,
        "",
    ])

    return "\n".join(lines)


def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard.

    Returns:
        True if successful, False otherwise
    """
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="vv",
        description="Verbatim voice transcription using Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  vv                    Interactive mode with base model
  vv -m large           Use large model for better accuracy
  vv -1 -c              Single recording, copy to clipboard
  vv -q | pbcopy        Quiet mode, pipe to clipboard (macOS)
  vv -o transcript.txt  Save transcription to file
  vv -l en              Force English (skip auto-detection)
""",
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "-m", "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
        help="Whisper model size (default: base)",
    )

    parser.add_argument(
        "-l", "--language",
        default=None,
        help="Force language (e.g., en, es, fr). Default: auto-detect",
    )

    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Write transcription to file",
    )

    parser.add_argument(
        "-c", "--copy",
        action="store_true",
        help="Copy transcription to clipboard",
    )

    parser.add_argument(
        "-1", "--once",
        action="store_true",
        help="Single recording, then exit",
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Output only transcription (no UI)",
    )

    parser.add_argument(
        "--timestamps",
        action="store_true",
        help="Include segment timestamps in output",
    )

    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="Show available audio devices and exit",
    )

    return parser


def main() -> int:
    """Main entry point for vv CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle --list-devices
    if args.list_devices:
        print(list_devices())
        return 0

    # Initialize backend and load model
    backend = get_backend()

    if not args.quiet:
        print("=" * 50)
        print("  vv - VIBEVOX")
        print("=" * 50)
        print(f"\nBackend: {backend.name}")
        print(f"Model: {args.model}")
        print("Loading model...")

    backend.load_model(args.model)

    if not args.quiet:
        print("Model loaded.\n")

    session_count = 0

    try:
        while True:
            session_count += 1

            if not args.quiet:
                prompt = "Press Enter to start recording"
                if not args.once:
                    prompt += " (Ctrl+C to quit)"
                print(f"[Session {session_count}] {prompt}...")
                input()

            # Record audio
            audio_data, duration, sample_rate = record_audio(
                sample_rate=16000,
                quiet=args.quiet,
            )

            if len(audio_data) == 0:
                if not args.quiet:
                    print("No audio recorded. Try again.\n")
                if args.once:
                    return 1
                continue

            if not args.quiet:
                print("Transcribing...")

            # Transcribe
            result = backend.transcribe(
                audio_data,
                language=args.language,
                word_timestamps=args.timestamps,
            )

            # Format output
            output = format_output(
                result,
                duration,
                show_timestamps=args.timestamps,
                quiet=args.quiet,
            )

            # Handle output destinations
            if args.output:
                try:
                    with open(args.output, "a") as f:
                        f.write(output)
                        if not output.endswith("\n"):
                            f.write("\n")
                    if not args.quiet:
                        print(f"Saved to {args.output}")
                except OSError as e:
                    print(f"Error writing to file: {e}", file=sys.stderr)
                    return 1
            else:
                print(output)

            # Copy to clipboard if requested
            if args.copy:
                text_to_copy = result.text
                if args.timestamps and result.segments:
                    lines = []
                    for seg in result.segments:
                        start = format_timestamp(seg["start"])
                        end = format_timestamp(seg["end"])
                        lines.append(f"[{start}-{end}] {seg['text']}")
                    text_to_copy = "\n".join(lines)

                if copy_to_clipboard(text_to_copy):
                    if not args.quiet:
                        print("Copied to clipboard.")
                else:
                    print("Warning: Could not copy to clipboard", file=sys.stderr)

            # Exit if single-shot mode
            if args.once:
                return 0

    except KeyboardInterrupt:
        if not args.quiet:
            print("\n\nGoodbye!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
