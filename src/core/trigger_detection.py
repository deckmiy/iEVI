"""
Trigger detection module for adaptive piston algorithm.
Implements clogging detection based on pressure slope thresholds.
"""

from collections import deque
from typing import List, Tuple

from .slope_calculation import calculate_slope_window


def detect_triggers(
    pressure_series: List[float],
    timestamp_series: List[float],
    slope_threshold: float = 20.0,
    grace_period: float = 5.0,
    min_trigger_interval: float = 13.0,
    window_size: int = 5
) -> List[Tuple[float, float, float]]:
    """
    Detect trigger points in pressure time series based on slope analysis.
    
    Args:
        pressure_series: List of pressure values
        timestamp_series: Corresponding list of timestamps (seconds)
        slope_threshold: Slope threshold for clogging detection (pressure/second)
        grace_period: Grace period after start (seconds) - no detection during this time
        min_trigger_interval: Minimum interval between triggers (seconds)
        window_size: Size of sliding window for slope calculation (default: 5)
    
    Returns:
        List of trigger points, each as (trigger_time, trigger_index, average_slope)
    
    Raises:
        ValueError: When pressure series and timestamp series have different lengths
    
    Algorithm:
        1. Skip points during grace period
        2. Maintain a sliding window of recent pressure points
        3. When window is full, calculate average slope
        4. Trigger if slope exceeds threshold and minimum interval has passed
    """
    if len(pressure_series) != len(timestamp_series):
        raise ValueError("Pressure series and timestamp series must have the same length")
    
    triggers = []
    last_trigger_time = -min_trigger_interval  # Ensure first trigger can be detected
    window = deque(maxlen=window_size)
    
    for idx, (pressure, timestamp) in enumerate(zip(pressure_series, timestamp_series)):
        # Skip points during grace period
        if timestamp < grace_period:
            window.append((timestamp, pressure))
            continue
        
        window.append((timestamp, pressure))
        
        # Calculate slope when window is full
        if len(window) == window_size:
            window_timestamps = [t for t, _ in window]
            window_pressures = [p for _, p in window]
            
            avg_slope = calculate_slope_window(window_pressures, window_timestamps)
            
            # Check trigger conditions
            if avg_slope >= slope_threshold:
                trigger_time = window_timestamps[-1]  # Use last point in window as trigger time
                if trigger_time - last_trigger_time >= min_trigger_interval:
                    triggers.append((trigger_time, idx, avg_slope))
                    last_trigger_time = trigger_time
    
    return triggers