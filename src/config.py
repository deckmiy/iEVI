"""
Configuration module for the Adaptive Piston Algorithm.
Provides centralized parameter management for all algorithm components.

This module can be used in two ways:
1. Import default_config directly: from src.config import default_config
2. Create custom config: from src.config import Config; my_config = Config()

Example usage:
    from src.config import default_config
    print(default_config.slope_threshold)
    
    # Or create a custom configuration
    custom_config = Config(
        slope_threshold=25.0,
        grace_period=3.0,
        backflush_flow_ml_hr=12.0
    )
"""

from typing import Dict, Any
import json
import os


class Config:
    """
    Configuration class for Adaptive Piston Algorithm parameters.
    
    This class provides a centralized way to manage all algorithm parameters
    including detection thresholds, backflush settings, and visualization options.
    """
    
    def __init__(
        self,
        # Detection parameters
        slope_threshold: float = 20.0,
        grace_period: float = 5.0,
        min_trigger_interval: float = 13.0,
        sliding_window_size: int = 5,
        
        # Backflush parameters
        backflush_volume_ml: float = 0.1,
        backflush_flow_ml_hr: float = 10.0,
        backflush_pressure_drop: float = 30.0,  # Pressure drop during backflush (percentage)
        
        # Data simulation parameters
        simulation_duration: float = 120.0,
        simulation_sample_rate: float = 1.0,
        simulation_baseline_pressure: float = 100.0,
        simulation_noise_std: float = 1.5,
        simulation_clog_events: list = None,
        

        
        # Output parameters
        default_output_csv: str = "trigger_results.csv",
        quiet_mode: bool = False,
        
        # Advanced parameters
        enable_adaptive_threshold: bool = False,
        adaptive_threshold_window: int = 100,
        enable_noise_filtering: bool = True,
        noise_filter_window: int = 3,
    ):
        """
        Initialize configuration with default or custom values.
        
        Args:
            slope_threshold: Pressure slope threshold for clogging detection (pressure/s)
            grace_period: Grace period after startup (seconds)
            min_trigger_interval: Minimum time between consecutive triggers (seconds)
            sliding_window_size: Size of sliding window for slope calculation
            
            backflush_volume_ml: Backflush volume in milliliters
            backflush_flow_ml_hr: Backflush flow rate in milliliters per hour
            backflush_pressure_drop: Pressure drop percentage during backflush
            
            simulation_duration: Duration for simulated data (seconds)
            simulation_sample_rate: Sample rate for simulated data (Hz)
            simulation_baseline_pressure: Baseline pressure for simulation
            simulation_noise_std: Standard deviation of noise in simulation
            simulation_clog_events: List of clog events for simulation
            

            
            default_output_csv: Default filename for CSV output
            quiet_mode: Whether to suppress console output
            
            enable_adaptive_threshold: Enable adaptive threshold adjustment
            adaptive_threshold_window: Window size for adaptive threshold calculation
            enable_noise_filtering: Enable noise filtering for pressure data
            noise_filter_window: Window size for noise filtering
        """
        # Detection parameters
        self.slope_threshold = slope_threshold
        self.grace_period = grace_period
        self.min_trigger_interval = min_trigger_interval
        self.sliding_window_size = sliding_window_size
        
        # Backflush parameters
        self.backflush_volume_ml = backflush_volume_ml
        self.backflush_flow_ml_hr = backflush_flow_ml_hr
        self.backflush_pressure_drop = backflush_pressure_drop
        
        # Calculate backflush duration (derived parameter)
        self.backflush_duration = self._calculate_backflush_duration()
        
        # Data simulation parameters
        self.simulation_duration = simulation_duration
        self.simulation_sample_rate = simulation_sample_rate
        self.simulation_baseline_pressure = simulation_baseline_pressure
        self.simulation_noise_std = simulation_noise_std
        self.simulation_clog_events = simulation_clog_events or [
            (25.0, 6.0, 35.0),  # (start_time, duration, slope)
            (55.0, 7.0, 28.0),
            (85.0, 8.0, 32.0)
        ]
        

        
        # Output parameters
        self.default_output_csv = default_output_csv
        self.quiet_mode = quiet_mode
        
        # Advanced parameters
        self.enable_adaptive_threshold = enable_adaptive_threshold
        self.adaptive_threshold_window = adaptive_threshold_window
        self.enable_noise_filtering = enable_noise_filtering
        self.noise_filter_window = noise_filter_window
    
    def _calculate_backflush_duration(self) -> float:
        """
        Calculate backflush duration based on volume and flow rate.
        
        Returns:
            Backflush duration in seconds
        """
        if self.backflush_flow_ml_hr <= 1e-6:
            return 0.0
        
        duration_hr = self.backflush_volume_ml / self.backflush_flow_ml_hr
        return duration_hr * 3600.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            # Detection parameters
            'slope_threshold': self.slope_threshold,
            'grace_period': self.grace_period,
            'min_trigger_interval': self.min_trigger_interval,
            'sliding_window_size': self.sliding_window_size,
            
            # Backflush parameters
            'backflush_volume_ml': self.backflush_volume_ml,
            'backflush_flow_ml_hr': self.backflush_flow_ml_hr,
            'backflush_pressure_drop': self.backflush_pressure_drop,
            'backflush_duration': self.backflush_duration,
            
            # Data simulation parameters
            'simulation_duration': self.simulation_duration,
            'simulation_sample_rate': self.simulation_sample_rate,
            'simulation_baseline_pressure': self.simulation_baseline_pressure,
            'simulation_noise_std': self.simulation_noise_std,
            'simulation_clog_events': self.simulation_clog_events,
            

            
            # Output parameters
            'default_output_csv': self.default_output_csv,
            'quiet_mode': self.quiet_mode,
            
            # Advanced parameters
            'enable_adaptive_threshold': self.enable_adaptive_threshold,
            'adaptive_threshold_window': self.adaptive_threshold_window,
            'enable_noise_filtering': self.enable_noise_filtering,
            'noise_filter_window': self.noise_filter_window,
        }
    
    def save_to_json(self, filepath: str) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            filepath: Path to save JSON file
        """
        config_dict = self.to_dict()
        
        # Convert non-serializable values
        serializable_dict = {}
        for key, value in config_dict.items():
            if isinstance(value, tuple):
                serializable_dict[key] = list(value)
            else:
                serializable_dict[key] = value
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_dict, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_json(cls, filepath: str) -> 'Config':
        """
        Load configuration from JSON file.
        
        Args:
            filepath: Path to JSON configuration file
            
        Returns:
            Config instance with loaded parameters
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        
        # Remove derived parameters that shouldn't be passed to constructor
        # backflush_duration is calculated from volume and flow rate
        config_dict.pop('backflush_duration', None)
        

        
        return cls(**config_dict)
    
    def update_from_dict(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration from dictionary.
        
        Args:
            updates: Dictionary with parameter updates
        """
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Recalculate derived parameters
        if 'backflush_volume_ml' in updates or 'backflush_flow_ml_hr' in updates:
            self.backflush_duration = self._calculate_backflush_duration()
    
    def __str__(self) -> str:
        """String representation of configuration."""
        lines = ["Adaptive Piston Algorithm Configuration", "=" * 50]
        
        sections = [
            ("Detection Parameters", [
                f"  Slope Threshold: {self.slope_threshold} pressure/s",
                f"  Grace Period: {self.grace_period} s",
                f"  Minimum Trigger Interval: {self.min_trigger_interval} s",
                f"  Sliding Window Size: {self.sliding_window_size} points",
            ]),
            ("Backflush Parameters", [
                f"  Backflush Volume: {self.backflush_volume_ml} ml",
                f"  Backflush Flow Rate: {self.backflush_flow_ml_hr} ml/hr",
                f"  Backflush Duration: {self.backflush_duration:.2f} s",
                f"  Backflush Pressure Drop: {self.backflush_pressure_drop}%",
            ]),

            ("Output Parameters", [
                f"  Default Output CSV: {self.default_output_csv}",
                f"  Quiet Mode: {self.quiet_mode}",
            ]),
        ]
        
        for section_name, section_lines in sections:
            lines.append(f"\n{section_name}")
            lines.extend(section_lines)
        
        return "\n".join(lines)


# Default configuration instance
default_config = Config()

# Example configurations for different use cases
sensitive_config = Config(
    slope_threshold=15.0,
    grace_period=3.0,
    min_trigger_interval=10.0,
    backflush_flow_ml_hr=12.0,
    backflush_volume_ml=0.15,
)

conservative_config = Config(
    slope_threshold=25.0,
    grace_period=7.0,
    min_trigger_interval=15.0,
    backflush_flow_ml_hr=8.0,
    backflush_volume_ml=0.08,
)

test_config = Config(
    slope_threshold=1.0,
    grace_period=0.0,
    min_trigger_interval=5.0,
    backflush_flow_ml_hr=10.0,
    backflush_volume_ml=0.1,
    simulation_duration=60.0,
    quiet_mode=True,
)