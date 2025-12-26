"""SDR Controller Interface for listening to AM and FM frequencies."""
import logging
import numpy as np
from typing import Optional, Tuple
from datetime import datetime
import random

# Optional dependencies - import with fallback
try:
    from rtlsdr import RtlSdr
    RTLSDR_AVAILABLE = True
except ImportError:
    RTLSDR_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

try:
    from scipy import signal as scipy_signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

logger = logging.getLogger(__name__)

# Simulation mode constants
SIMULATION_SIGNAL_MIN_DB = -80.0
SIMULATION_SIGNAL_MAX_DB = -30.0


class SDRController:
    """Interface to Software Defined Radio for frequency scanning and recording."""
    
    def __init__(self, sample_rate: int = 2400000, gain: str = "auto"):
        """
        Initialize SDR Controller.
        
        Args:
            sample_rate: Sample rate in Hz
            gain: Gain setting ('auto' or specific value)
        """
        self.sample_rate = sample_rate
        self.gain = gain
        self.sdr = None
        self._initialized = False
        
    def initialize(self) -> bool:
        """
        Initialize the SDR device.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not RTLSDR_AVAILABLE:
                logger.warning("rtlsdr library not available, using simulation mode")
                self._initialized = True  # Allow simulation mode
                return True
            
            self.sdr = RtlSdr()
            self.sdr.sample_rate = self.sample_rate
            
            if self.gain == "auto":
                self.sdr.gain = 'auto'
            else:
                self.sdr.gain = float(self.gain)
            
            self._initialized = True
            logger.info(f"SDR initialized with sample_rate={self.sample_rate}, gain={self.gain}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize SDR: {e}")
            return False
    
    def tune_frequency(self, frequency: int) -> bool:
        """
        Tune to a specific frequency.
        
        Args:
            frequency: Frequency in Hz
            
        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            logger.error("SDR not initialized")
            return False
            
        try:
            if self.sdr:
                self.sdr.center_freq = frequency
            logger.info(f"Tuned to frequency: {frequency} Hz ({self._format_frequency(frequency)})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to tune to {frequency}: {e}")
            return False
    
    def detect_signal(self, frequency: int, threshold: float = -50.0, duration: int = 5) -> Tuple[bool, float]:
        """
        Detect if there's an active signal on a frequency.
        
        Args:
            frequency: Frequency to check in Hz
            threshold: Signal strength threshold in dB
            duration: Duration to sample in seconds
            
        Returns:
            Tuple of (is_active, signal_strength)
        """
        if not self.tune_frequency(frequency):
            return False, -100.0
        
        try:
            if self.sdr:
                # Read samples from SDR
                samples = self.sdr.read_samples(self.sample_rate * duration)
                
                # Calculate power spectrum
                power = np.abs(np.fft.fft(samples)) ** 2
                power_db = 10 * np.log10(power + 1e-10)
                
                # Get peak signal strength
                signal_strength = float(np.max(power_db))
            else:
                # Simulation mode - generate random signal strength
                signal_strength = random.uniform(SIMULATION_SIGNAL_MIN_DB, SIMULATION_SIGNAL_MAX_DB)
            
            is_active = signal_strength > threshold
            
            logger.info(f"Frequency {self._format_frequency(frequency)}: "
                       f"Signal={signal_strength:.2f}dB, Active={is_active}")
            
            return is_active, signal_strength
            
        except Exception as e:
            logger.error(f"Error detecting signal on {frequency}: {e}")
            return False, -100.0
    
    def record_frequency(self, frequency: int, duration: int, output_file: str) -> bool:
        """
        Record audio from a frequency.
        
        Args:
            frequency: Frequency to record in Hz
            duration: Duration in seconds
            output_file: Path to save the recording
            
        Returns:
            True if successful, False otherwise
        """
        if not self.tune_frequency(frequency):
            return False
        
        try:
            if not SOUNDFILE_AVAILABLE:
                raise ImportError("soundfile library not available")
            
            if self.sdr:
                # Record from SDR
                samples = self.sdr.read_samples(self.sample_rate * duration)
                
                # Demodulate based on frequency range
                if frequency < 30000000:  # AM
                    audio = self._demodulate_am(samples)
                else:  # FM
                    audio = self._demodulate_fm(samples)
            else:
                # Simulation mode - generate silence or noise
                audio = np.random.randn(16000 * duration) * 0.01
            
            # Resample to 16kHz for speech recognition
            audio_resampled = self._resample_audio(audio, 16000)
            
            # Save to file
            sf.write(output_file, audio_resampled, 16000)
            
            logger.info(f"Recorded {duration}s from {self._format_frequency(frequency)} to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording from {frequency}: {e}")
            return False
    
    def _demodulate_am(self, samples: np.ndarray) -> np.ndarray:
        """Demodulate AM signal."""
        # Simple envelope detection
        return np.abs(samples)
    
    def _demodulate_fm(self, samples: np.ndarray) -> np.ndarray:
        """Demodulate FM signal."""
        # Simple FM demodulation using phase differences
        phase = np.angle(samples)
        audio = np.diff(np.unwrap(phase))
        return audio
    
    def _resample_audio(self, audio: np.ndarray, target_rate: int) -> np.ndarray:
        """Resample audio to target sample rate."""
        if not SCIPY_AVAILABLE:
            # Simple downsampling if scipy not available
            original_rate = self.sample_rate
            step = int(original_rate / target_rate)
            return audio[::step].astype(np.float32)
        
        # Calculate resampling ratio
        original_rate = self.sample_rate
        resample_ratio = target_rate / original_rate
        
        # Resample
        num_samples = int(len(audio) * resample_ratio)
        resampled = scipy_signal.resample(audio, num_samples)
        
        # Normalize
        if np.max(np.abs(resampled)) > 0:
            resampled = resampled / np.max(np.abs(resampled))
        
        return resampled.astype(np.float32)
    
    def _format_frequency(self, freq: int) -> str:
        """Format frequency for display."""
        if freq < 30000000:  # AM range
            return f"{freq / 1000:.0f} kHz (AM)"
        else:  # FM range
            return f"{freq / 1000000:.1f} MHz (FM)"
    
    def close(self):
        """Close the SDR connection."""
        if self.sdr:
            try:
                self.sdr.close()
                logger.info("SDR connection closed")
            except Exception as e:
                logger.error(f"Error closing SDR: {e}")
        
        self._initialized = False
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
