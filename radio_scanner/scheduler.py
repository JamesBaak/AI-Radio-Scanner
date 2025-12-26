"""Scheduler for periodic summarization tasks."""
import logging
import schedule
import time
from datetime import datetime
from .summarization import SummarizationService
from .config import Config

logger = logging.getLogger(__name__)


class SummaryScheduler:
    """Scheduler for running summarization jobs."""
    
    def __init__(self, config: Config, summarization_service: SummarizationService):
        """
        Initialize summary scheduler.
        
        Args:
            config: Configuration object
            summarization_service: Summarization service instance
        """
        self.config = config
        self.summarization_service = summarization_service
        self.running = False
    
    def run_summary_job(self):
        """Execute the summary job."""
        logger.info("Starting scheduled summary job...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = f"{self.config.SUMMARY_DIR}/summary_{timestamp}.md"
        
        success = self.summarization_service.summarize_transcripts_from_directory(
            self.config.TRANSCRIPT_DIR,
            summary_file
        )
        
        if success:
            logger.info(f"Summary job completed successfully: {summary_file}")
        else:
            logger.warning("Summary job completed with no results")
    
    def schedule_hourly(self):
        """Schedule the summary job to run every hour."""
        # Schedule to run at the specified hour minute
        hour = self.config.SUMMARY_SCHEDULE_HOUR
        schedule.every(hour).hours.do(self.run_summary_job)
        
        logger.info(f"Scheduled summary job to run every {hour} hour(s)")
    
    def start(self, blocking: bool = True):
        """
        Start the scheduler.
        
        Args:
            blocking: If True, run in blocking mode; if False, run once and return
        """
        self.running = True
        logger.info("Summary scheduler started")
        
        if blocking:
            # Run continuously
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        else:
            # Run pending jobs once
            schedule.run_pending()
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        logger.info("Summary scheduler stopped")
    
    def run_now(self):
        """Run the summary job immediately."""
        logger.info("Running summary job on demand...")
        self.run_summary_job()
