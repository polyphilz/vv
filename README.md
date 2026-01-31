# vv (VibeVox)

[![CI](https://github.com/polyphilz/vv/actions/workflows/ci.yml/badge.svg)](https://github.com/polyphilz/vv/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img src="assets/demo.gif" alt="vv demo" width="600">
</p>

Verbatim voice transcription CLI using Whisper. Records from your microphone and transcribes speech to text locally.

## Features

- **Verbatim transcription** - Keeps "um", "uh", filler words exactly as spoken
- **Local processing** - No cloud APIs, everything runs on your machine
- **Apple Silicon optimized** - Uses MLX backend on M1/M2/M3 Macs for 10x faster inference
- **Multiple output options** - Print to terminal, save to file, or copy to clipboard

## Privacy

All audio processing happens **locally on your machine**. No data is ever sent to external servers.

- Audio is recorded to memory only (never written to disk unless you use `-o`)
- Whisper models run entirely offline after initial download
- No telemetry, analytics, or network requests

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/polyphilz/vv/main/install.sh | bash
```

Or install manually:

```bash
# Using uv (recommended)
uv tool install git+https://github.com/polyphilz/vv

# Using pipx
pipx install git+https://github.com/polyphilz/vv

# On Apple Silicon, install with MLX support for best performance
uv tool install 'vv[apple] @ git+https://github.com/polyphilz/vv'
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
git clone https://github.com/polyphilz/vv
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

## Troubleshooting

### macOS: "Could not access microphone"

Grant microphone permission to your terminal app:
1. Open System Preferences > Security & Privacy > Privacy > Microphone
2. Add and enable your terminal (Terminal.app, iTerm2, etc.)

### Linux: `PortAudio library not found`

Install PortAudio:

```bash
# Ubuntu/Debian
sudo apt install libportaudio2

# Fedora
sudo dnf install portaudio

# Arch
sudo pacman -S portaudio
```

### First run is slow

The first run downloads the Whisper model (~140MB for base). Subsequent runs are instant.

### No audio devices found

```bash
# List available devices
vv --list-devices

# If empty, check that your microphone is connected and recognized by the OS
```

### Transcription quality is poor

- Try a larger model: `vv -m large`
- Speak clearly and reduce background noise
- Force language if auto-detect fails: `vv -l en`

### MLX backend not loading on Apple Silicon

Ensure you installed with Apple extras:

```bash
uv tool install 'vv[apple] @ git+https://github.com/polyphilz/vv'
```

## License

MIT
