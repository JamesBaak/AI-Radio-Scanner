"""Summarization service using OpenAI API."""
import logging
import os
from typing import List, Optional
from datetime import datetime
import glob

logger = logging.getLogger(__name__)


class SummarizationService:
    """Service for summarizing transcripts using OpenAI."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize summarization service.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
        """
        self.api_key = api_key
        self.model = model
        self.client = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the OpenAI client.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.api_key:
            logger.warning("OpenAI API key not set, using mock summarization")
            self._initialized = True  # Allow mock mode
            return True
        
        try:
            from openai import OpenAI
            
            self.client = OpenAI(api_key=self.api_key)
            self._initialized = True
            logger.info(f"OpenAI client initialized with model: {self.model}")
            return True
            
        except ImportError:
            logger.warning("OpenAI library not available, using mock summarization")
            self._initialized = True  # Allow mock mode
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return False
    
    def summarize_transcript(self, transcript: str) -> Optional[str]:
        """
        Summarize a single transcript.
        
        Args:
            transcript: Text to summarize
            
        Returns:
            Summary text or None if failed
        """
        if not self._initialized:
            logger.error("Summarization service not initialized")
            return None
        
        if not transcript or len(transcript.strip()) == 0:
            logger.warning("Empty transcript provided")
            return "No content to summarize."
        
        try:
            if self.client:
                # Use OpenAI for summarization
                logger.info("Generating summary with OpenAI...")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that summarizes radio transcripts. Provide concise, informative summaries highlighting key points, topics discussed, and any important information."},
                        {"role": "user", "content": f"Please summarize this radio transcript:\n\n{transcript}"}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                summary = response.choices[0].message.content
            else:
                # Mock summarization
                logger.warning("Using mock summarization")
                word_count = len(transcript.split())
                summary = f"[Mock Summary] This transcript contains approximately {word_count} words. " \
                         f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
            
            logger.info(f"Summary generated: {len(summary)} characters")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None
    
    def summarize_transcripts_from_directory(self, transcript_dir: str, output_file: str) -> bool:
        """
        Summarize all transcripts in a directory.
        
        Args:
            transcript_dir: Directory containing transcript files
            output_file: Path to save the combined summary
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(transcript_dir):
            logger.error(f"Transcript directory not found: {transcript_dir}")
            return False
        
        # Find all transcript files
        transcript_files = glob.glob(os.path.join(transcript_dir, "*.txt"))
        
        if not transcript_files:
            logger.warning(f"No transcript files found in {transcript_dir}")
            return False
        
        logger.info(f"Found {len(transcript_files)} transcript files to summarize")
        
        summaries = []
        
        for transcript_file in sorted(transcript_files):
            try:
                # Read transcript
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    transcript = f.read()
                
                # Generate summary
                summary = self.summarize_transcript(transcript)
                
                if summary:
                    file_name = os.path.basename(transcript_file)
                    summaries.append(f"### {file_name}\n{summary}\n")
                    
            except Exception as e:
                logger.error(f"Error processing {transcript_file}: {e}")
                continue
        
        if summaries:
            # Combine all summaries
            combined_summary = f"# Radio Transcript Summary\n"
            combined_summary += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            combined_summary += f"Total Transcripts: {len(summaries)}\n\n"
            combined_summary += "\n".join(summaries)
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(combined_summary)
            
            logger.info(f"Combined summary saved to {output_file}")
            return True
        
        return False
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Clean up if needed
        pass
