# Example Usage Scenarios

## Scenario 1: Emergency Services Monitoring

Monitor emergency service frequencies for important broadcasts:

```bash
# 1. Configure frequencies in .env
AM_FREQUENCIES=530000,1610000  # Weather radio
FM_FREQUENCIES=154650000,155475000  # Public safety

# 2. Run continuous monitoring
python run.py monitor
```

**Output:**
- Automatically records when activity detected
- Generates transcripts of broadcasts
- Creates hourly summaries of all traffic
- Logs saved to `radio_scanner.log`

## Scenario 2: News & Information Gathering

Scan news radio stations and generate daily summaries:

```bash
# 1. Configure news frequencies
AM_FREQUENCIES=640000,880000,1010000  # News stations
FM_FREQUENCIES=90300000,93100000  # NPR/News

# 2. Run one-time scan
python run.py scan

# 3. Generate summary
python run.py summarize
```

**Workflow:**
1. System scans configured frequencies
2. Records active broadcasts (30 seconds each)
3. Transcribes audio to text
4. Generates AI summary of key points

## Scenario 3: Aviation Communications

Monitor aviation frequencies for flight operations:

```bash
# Configure aviation frequencies
AM_FREQUENCIES=118100000,121500000,126200000  # Tower, Ground, ATIS

# Set higher signal threshold for clarity
SIGNAL_THRESHOLD=-45.0

# Run monitoring
python run.py monitor
```

## Scenario 4: Amateur Radio Activity

Track amateur radio conversations and nets:

```bash
# Configure ham frequencies
FM_FREQUENCIES=145510000,146520000,147300000  # 2m simplex/repeaters

# Scan every 2 minutes
SCAN_INTERVAL_SECONDS=120

# Summarize every 30 minutes
SUMMARY_SCHEDULE_HOUR=0.5

python run.py monitor
```

## Scenario 5: Research & Analysis

Collect data from multiple frequencies for research:

```python
# Custom script using the library
from radio_scanner.config import Config
from radio_scanner.scanner import RadioScanner
from radio_scanner.summarization import SummarizationService

# Initialize
with RadioScanner(Config) as scanner:
    # Scan frequencies
    results = scanner.scan_frequencies()
    
    # Process each active frequency
    for frequency, signal, is_active in results:
        if is_active:
            print(f"Recording {frequency}...")
            scanner.record_and_transcribe_frequency(frequency, duration=60)
    
    # Generate summary
    summarizer = SummarizationService(Config.OPENAI_API_KEY)
    summarizer.initialize()
    summarizer.summarize_transcripts_from_directory(
        Config.TRANSCRIPT_DIR,
        "research_summary.md"
    )
```

## Scenario 6: Testing Without Hardware

Test the system without SDR hardware:

```bash
# The system automatically runs in simulation mode
# when rtlsdr library is not available

# Test scan
python run.py scan

# Expected output:
# - Random signal strengths generated
# - Mock audio files created
# - Sample transcripts generated
# - Full workflow demonstrated
```

## Scenario 7: Production Deployment

Deploy for 24/7 monitoring:

```bash
# 1. Install on server
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
nano .env  # Set API keys and frequencies

# 3. Run as background service
nohup python run.py monitor > output.log 2>&1 &

# 4. Monitor logs
tail -f radio_scanner.log
```

## Scenario 8: Batch Processing

Process historical recordings:

```bash
# 1. Place audio files in recordings/
# (files should be named with format: YYYYMMDD_HHMMSS_FREQUENCY.wav)

# 2. Run transcription manually
python -c "
from radio_scanner.transcription import TranscriptionService
import glob

transcriber = TranscriptionService()
transcriber.initialize()

for audio_file in glob.glob('./recordings/*.wav'):
    transcript_file = audio_file.replace('recordings', 'transcripts').replace('.wav', '.txt')
    transcriber.transcribe_audio(audio_file, transcript_file)
"

# 3. Generate summary
python run.py summarize
```

## Tips & Best Practices

### Frequency Selection
- Start with fewer frequencies to test
- Add more as you understand signal patterns
- Use signal threshold to filter noise

### Recording Quality
- Adjust `SIGNAL_THRESHOLD` based on your environment
- Lower values capture more but may include noise
- Higher values only capture strong signals

### Summarization
- Run hourly summaries for real-time monitoring
- Generate on-demand summaries for specific periods
- Review summaries to identify important events

### Performance
- Simulation mode uses minimal resources
- Real SDR mode requires USB 2.0+ for bandwidth
- Transcription is CPU-intensive (consider GPU for Whisper)

### Storage
- Audio files: ~6KB per 30 seconds (16kHz mono)
- Transcripts: ~1KB per minute of speech
- Plan storage based on recording frequency

## Advanced Configuration

### Custom Scan Pattern
```python
# Scan specific frequencies at different intervals
from radio_scanner.scanner import RadioScanner
from radio_scanner.config import Config
import time

with RadioScanner(Config) as scanner:
    while True:
        # High priority frequencies (every minute)
        for freq in [121500000, 126200000]:  # Aviation
            scanner.sdr.detect_signal(freq)
        time.sleep(60)
        
        # Low priority frequencies (every 5 minutes)
        for freq in Config.FM_FREQUENCIES:
            scanner.sdr.detect_signal(freq)
        time.sleep(240)
```

### Custom Summarization
```python
# Generate custom summaries with specific prompts
from radio_scanner.summarization import SummarizationService

summarizer = SummarizationService(api_key="your_key")
summarizer.initialize()

transcript = "..." # Your transcript
summary = summarizer.summarize_transcript(transcript)
```

## Troubleshooting

### No Active Frequencies
- Lower `SIGNAL_THRESHOLD`
- Check antenna connection
- Verify frequency is correct
- In simulation mode, signals are random

### Poor Transcription Quality
- Check audio recording quality
- Ensure sufficient recording duration
- Consider using larger Whisper model
- Filter background noise

### Missing Summaries
- Verify OpenAI API key is set
- Check transcript directory has files
- Review API quota limits
- System falls back to mock summaries if API fails
