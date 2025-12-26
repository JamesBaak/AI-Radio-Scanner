# Quick Start Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### 1. One-Time Frequency Scan

Scan all configured frequencies and process active ones:

```bash
python run.py scan
```

This will:
- Scan AM frequencies: 530kHz, 1000kHz, 1500kHz
- Scan FM frequencies: 88.1MHz, 95.5MHz, 101.1MHz, 107.9MHz
- Detect active signals
- Record and transcribe active frequencies

### 2. Generate Summary

Create a summary of all transcripts:

```bash
python run.py summarize
```

### 3. Continuous Monitoring

Run continuous monitoring with hourly summaries:

```bash
python run.py monitor
```

Press Ctrl+C to stop.

## Configuration

Edit `.env` file to customize:

```bash
# Copy example configuration
cp .env.example .env

# Edit with your settings
nano .env
```

Key settings:
- `OPENAI_API_KEY`: Your OpenAI API key for summarization
- `AM_FREQUENCIES`: Comma-separated AM frequencies in Hz
- `FM_FREQUENCIES`: Comma-separated FM frequencies in Hz
- `SIGNAL_THRESHOLD`: Signal strength threshold in dB (default: -50.0)
- `SUMMARY_SCHEDULE_HOUR`: Hours between summaries (default: 1)

## Output Files

- `recordings/`: Audio files (.wav)
- `transcripts/`: Text transcripts (.txt)
- `summaries/`: AI-generated summaries (.md)
- `radio_scanner.log`: Application log

## Simulation Mode

The system runs in simulation mode when SDR hardware is not available:
- Generates random signal strengths
- Creates mock audio files
- Produces sample transcripts

This allows testing without physical hardware.

## Next Steps

1. Configure your frequencies in `.env`
2. Set up OpenAI API key for real summarization
3. Connect RTL-SDR hardware (optional)
4. Run in your preferred mode

## Troubleshooting

**No active frequencies found:**
- Lower the `SIGNAL_THRESHOLD` in `.env`
- In simulation mode, signals are random

**Mock transcripts/summaries:**
- Install Whisper: `pip install openai-whisper`
- Set `OPENAI_API_KEY` in `.env`

**Permission errors:**
- Ensure write permissions for `recordings/`, `transcripts/`, `summaries/`
