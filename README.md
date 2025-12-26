# AI-Radio-Scanner

An intelligent Software Defined Radio (SDR) scanner that monitors AM and FM frequencies, records active transmissions, generates transcripts using speech recognition, and produces AI-powered summaries.

## Features

- 🎛️ **SDR Controller Interface**: Listen to different AM and FM frequencies
- 🔍 **Activity Detection**: Automatically detect when frequencies are active
- 🎙️ **Audio Recording**: Record transmissions from active frequencies
- 📝 **Speech-to-Text**: Generate transcripts using OpenAI Whisper
- 🤖 **AI Summarization**: Create intelligent summaries using OpenAI GPT
- ⏰ **Scheduled Jobs**: Automatic hourly summarization of transcripts

## System Architecture

```
┌─────────────────┐
│  SDR Hardware   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│ SDR Controller  │────▶│ Frequency Detect │
└────────┬────────┘     └──────────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│ Audio Recorder  │────▶│   Transcriber    │
└─────────────────┘     └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   Summarizer     │
                        └──────────────────┘
```

## Installation

### Prerequisites

- Python 3.8 or higher
- RTL-SDR compatible hardware (optional - system supports simulation mode)
- OpenAI API key (for summarization)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/JamesBaak/AI-Radio-Scanner.git
cd AI-Radio-Scanner
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the application:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Set your OpenAI API key in `.env`:
```
OPENAI_API_KEY=your_api_key_here
```

## Configuration

Edit the `.env` file to customize:

- **Frequencies**: Configure AM and FM frequencies to monitor
- **Detection Settings**: Adjust signal threshold and detection duration
- **Recording Settings**: Set output directories
- **Summarization**: Configure schedule and OpenAI model

Example configuration:
```bash
# Frequencies to scan (in Hz)
AM_FREQUENCIES=530000,1000000,1500000
FM_FREQUENCIES=88100000,95500000,101100000,107900000

# Signal detection threshold (in dB)
SIGNAL_THRESHOLD=-50.0

# Summary generation interval (hours)
SUMMARY_SCHEDULE_HOUR=1
```

## Usage

The application supports three modes:

### 1. Scan Mode (One-Time Scan)

Scan all configured frequencies once and process active ones:

```bash
python run.py scan
# or
python -m radio_scanner.main scan
```

This will:
- Scan all configured AM/FM frequencies
- Detect which frequencies have active signals
- Record and transcribe active frequencies
- Display results

### 2. Monitor Mode (Continuous)

Continuously monitor frequencies with automatic hourly summaries:

```bash
python run.py monitor
# or
python -m radio_scanner.main monitor
```

This will:
- Continuously scan frequencies every 5 minutes
- Record and transcribe active frequencies
- Generate summaries every hour
- Run until stopped (Ctrl+C)

### 3. Summarize Mode (Generate Summary)

Generate a summary of all existing transcripts:

```bash
python run.py summarize
# or
python -m radio_scanner.main summarize
```

This will:
- Read all transcripts from the transcript directory
- Generate a consolidated summary
- Save to the summaries directory

## Directory Structure

```
AI-Radio-Scanner/
├── radio_scanner/          # Main package
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── sdr_controller.py  # SDR interface
│   ├── scanner.py         # Main scanner service
│   ├── transcription.py   # Speech-to-text service
│   ├── summarization.py   # AI summarization service
│   └── scheduler.py       # Task scheduler
├── recordings/            # Audio recordings
├── transcripts/           # Generated transcripts
├── summaries/             # AI-generated summaries
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── .env.example         # Example configuration
└── README.md            # This file
```

## How It Works

1. **Frequency Scanning**: The SDR controller tunes to each configured frequency and measures signal strength
2. **Activity Detection**: If signal strength exceeds the threshold, the frequency is marked as active
3. **Recording**: Active frequencies are recorded for a configurable duration
4. **Transcription**: Audio recordings are processed using OpenAI Whisper for speech-to-text
5. **Summarization**: Transcripts are summarized using OpenAI GPT on a scheduled basis

## Simulation Mode

If you don't have SDR hardware, the system automatically runs in simulation mode:
- Generates random signal strengths for detection
- Creates mock audio for testing
- Provides sample transcripts

This allows you to test the system without physical hardware.

## Output Examples

### Scan Results
```
============================================================
FREQUENCY SCAN RESULTS
============================================================
AM_530kHz            | Signal: -65.32 dB | Inactive
AM_1000kHz           | Signal: -42.15 dB | ACTIVE
FM_88.1MHz           | Signal: -55.78 dB | Inactive
FM_95.5MHz           | Signal: -38.92 dB | ACTIVE
============================================================
```

### Generated Files
- **Recordings**: `recordings/20231215_143052_FM_95_5MHz.wav`
- **Transcripts**: `transcripts/20231215_143052_FM_95_5MHz.txt`
- **Summaries**: `summaries/summary_20231215_150000.md`

## Logging

Application logs are written to:
- Console (stdout)
- `radio_scanner.log` file

## Dependencies

Key libraries used:
- `pyrtlsdr`: SDR hardware interface
- `numpy`, `scipy`: Signal processing
- `soundfile`: Audio file handling
- `openai-whisper`: Speech recognition
- `openai`: GPT-based summarization
- `schedule`: Task scheduling

## Troubleshooting

### SDR Not Detected
- Ensure RTL-SDR drivers are installed
- Check USB connection
- System will fall back to simulation mode

### No Transcripts Generated
- Check audio recording quality
- Verify Whisper model is downloaded
- Review logs for errors

### Summarization Fails
- Verify OpenAI API key is set
- Check API quota/limits
- System will use mock summaries as fallback

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- OpenAI Whisper for speech recognition
- RTL-SDR community for SDR support
- OpenAI for GPT-based summarization
