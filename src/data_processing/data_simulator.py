"""
Pressure data simulator for testing and demonstration.
Generates synthetic pressure data with configurable clogging events.
"""

import random
from typing import List, Tuple, Optional


def simulate_pressure_data(
    duration: float = 60.0,
    sample_rate: float = 1.0,
    baseline: float = 100.0,
    noise_std: float = 2.0,
    clog_events: Optional[List[Tuple[float, float, float]]] = None
) -> Tuple[List[float], List[float]]:
    """
    Generate synthetic pressure data for testing and demonstration.
    
    Args:
        duration: Data duration in seconds
        sample_rate: Sampling rate in Hz (samples per second)
        baseline: Baseline pressure value
        noise_std: Standard deviation of Gaussian noise
        clog_events: List of clogging events, each as (start_time, duration, slope_strength)
    
    Returns:
        Tuple of (timestamps, pressures)
    
    Example:
        >>> timestamps, pressures = simulate_pressure_data(
        ...     duration=120.0,
        ...     sample_rate=1.0,
        ...     baseline=100.0,
        ...     noise_std=1.5,
        ...     clog_events=[(25.0, 6.0, 35.0), (55.0, 7.0, 28.0)]
        ... )
    """
    if clog_events is None:
        clog_events = [(20.0, 5.0, 30.0), (40.0, 5.0, 25.0)]
    
    n_samples = int(duration * sample_rate)
    timestamps = [i / sample_rate for i in range(n_samples)]
    pressures = []
    
    for t in timestamps:
        pressure = baseline + random.gauss(0, noise_std)
        
        # Add clogging events
        for start_time, event_duration, slope_strength in clog_events:
            if start_time <= t < start_time + event_duration:
                # Linear increase to simulate clogging
                pressure += slope_strength * (t - start_time)
        
        pressures.append(pressure)
    
    return timestamps, pressures