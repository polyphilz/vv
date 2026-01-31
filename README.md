# vv (VibeVox)

Verbatim voice transcription CLI using Whisper. Records from your microphone and transcribes speech to text locally.

## Features

- **Verbatim transcription** - Keeps "um", "uh", filler words exactly as spoken
- **Local processing** - No cloud APIs, everything runs on your machine
- **Apple Silicon optimized** - Uses MLX backend on M1/M2/M3 Macs for 10x faster inference
- **Multiple output options** - Print to terminal, save to file, or copy to clipboard

## Installation

```bash
# Using uv (recommended)
uv tool install vv

# Or with pip
pip install vv

# On Apple Silicon, install with MLX support for best performance
uv tool install 'vv[apple]'
```

## Usage

```bash
# Interactive mode (press Enter to start/stop recording, Ctrl+C to quit)
vv

# Single recording, copy result to clipboard
vv -1 -c

# Use larger model for better accuracy
vv -m large

# Save transcription to file
vv -o transcript.txt

# Quiet mode (output only text, good for piping)
vv -q | pbcopy

# Force English language (skip auto-detection)
vv -l en

# Show timestamps for each segment
vv --timestamps

# List available microphones
vv --list-devices
```

## Development

```bash
# Clone and run directly with uv
git clone https://github.com/rohan/vv
cd vv
uv run vv --help

# Run with Apple Silicon optimizations
uv run --extra apple vv
```

## Options

| Flag | Description |
|------|-------------|
| `-m, --model SIZE` | Model size: tiny, base, small, medium, large (default: base) |
| `-l, --language LANG` | Force language (e.g., en, es, fr). Default: auto-detect |
| `-o, --output FILE` | Write transcription to file |
| `-c, --copy` | Copy transcription to clipboard |
| `-1, --once` | Single recording, then exit |
| `-q, --quiet` | Output only transcription (no UI) |
| `--timestamps` | Include segment timestamps |
| `--list-devices` | Show available audio devices |
| `-v, --version` | Show version |
| `-h, --help` | Show help |

## Model Sizes

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | ~40MB | Fastest | Lower |
| base | ~140MB | Fast | Good |
| small | ~500MB | Medium | Better |
| medium | ~1.5GB | Slow | High |
| large | ~3GB | Slowest | Highest |

## Requirements

- Python 3.10+
- Working microphone
- For Apple Silicon: macOS with M1/M2/M3 chip (optional, for MLX acceleration)

## License

MIT
