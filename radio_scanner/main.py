"""Main application entry point for AI Radio Scanner."""
import logging
import argparse
import sys
import time
from datetime import datetime
from .config import Config
from .scanner import RadioScanner
from .summarization import SummarizationService
from .scheduler import SummaryScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('radio_scanner.log')
    ]
)

logger = logging.getLogger(__name__)


def scan_mode():
    """Run a single scan of all frequencies."""
    logger.info("=== Starting Frequency Scan Mode ===")
    
    with RadioScanner(Config) as scanner:
        # Scan for active frequencies
        results = scanner.scan_frequencies()
        
        # Display results
        print("\n" + "=" * 60)
        print("FREQUENCY SCAN RESULTS")
        print("=" * 60)
        for frequency, signal_strength, is_active in results:
            status = "ACTIVE" if is_active else "Inactive"
            freq_label = scanner._format_frequency_label(frequency)
            print(f"{freq_label:20s} | Signal: {signal_strength:6.2f} dB | {status}")
        print("=" * 60)
        
        # Process active frequencies
        if scanner.active_frequencies:
            print(f"\nProcessing {len(scanner.active_frequencies)} active frequency(ies)...")
            results = scanner.process_active_frequencies(duration=30)
            
            print("\n" + "=" * 60)
            print("RECORDING AND TRANSCRIPTION RESULTS")
            print("=" * 60)
            for frequency, recording_file, transcript_file in results:
                freq_label = scanner._format_frequency_label(frequency)
                print(f"{freq_label:20s}")
                print(f"  Recording:  {recording_file}")
                print(f"  Transcript: {transcript_file}")
            print("=" * 60)
        else:
            print("\nNo active frequencies found.")
    
    logger.info("=== Scan Mode Complete ===")


def monitor_mode():
    """Continuously monitor frequencies and generate hourly summaries."""
    logger.info("=== Starting Monitor Mode ===")
    
    # Initialize services
    summarization_service = SummarizationService(
        api_key=Config.OPENAI_API_KEY,
        model="gpt-3.5-turbo"
    )
    summarization_service.initialize()
    
    # Create scheduler
    scheduler = SummaryScheduler(Config, summarization_service)
    scheduler.schedule_hourly()
    
    print("\n" + "=" * 60)
    print("MONITOR MODE - Running Continuous Frequency Monitoring")
    print("=" * 60)
    print(f"Summary will be generated every {Config.SUMMARY_SCHEDULE_HOUR} hour(s)")
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    try:
        # Run scanner in a loop
        with RadioScanner(Config) as scanner:
            while True:
                logger.info("Running frequency scan cycle...")
                
                # Scan for active frequencies
                scanner.scan_frequencies()
                
                # Process active frequencies
                if scanner.active_frequencies:
                    scanner.process_active_frequencies(duration=30)
                
                # Check if it's time to summarize
                scheduler.start(blocking=False)
                
                # Wait before next scan (e.g., 5 minutes)
                logger.info("Waiting 5 minutes before next scan...")
                time.sleep(300)
                
    except KeyboardInterrupt:
        logger.info("Stopping monitor mode...")
        scheduler.stop()
    
    logger.info("=== Monitor Mode Complete ===")


def summarize_mode():
    """Generate a summary of all existing transcripts."""
    logger.info("=== Starting Summarization Mode ===")
    
    summarization_service = SummarizationService(
        api_key=Config.OPENAI_API_KEY,
        model="gpt-3.5-turbo"
    )
    summarization_service.initialize()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = f"{Config.SUMMARY_DIR}/summary_{timestamp}.md"
    
    print("\n" + "=" * 60)
    print("GENERATING SUMMARY")
    print("=" * 60)
    print(f"Transcript directory: {Config.TRANSCRIPT_DIR}")
    print(f"Output file: {summary_file}")
    print("=" * 60 + "\n")
    
    success = summarization_service.summarize_transcripts_from_directory(
        Config.TRANSCRIPT_DIR,
        summary_file
    )
    
    if success:
        print(f"\nSummary generated successfully: {summary_file}")
    else:
        print("\nNo transcripts found or summarization failed.")
    
    logger.info("=== Summarization Mode Complete ===")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="AI Radio Scanner - Monitor AM/FM frequencies and generate transcripts"
    )
    
    parser.add_argument(
        'mode',
        choices=['scan', 'monitor', 'summarize'],
        help='Operation mode: scan (one-time scan), monitor (continuous), or summarize (generate summary)'
    )
    
    args = parser.parse_args()
    
    # Ensure directories exist
    Config.ensure_directories()
    
    # Run appropriate mode
    if args.mode == 'scan':
        scan_mode()
    elif args.mode == 'monitor':
        monitor_mode()
    elif args.mode == 'summarize':
        summarize_mode()


if __name__ == "__main__":
    main()
