"""
Slope calculation module for adaptive piston algorithm.
Implements the five-point sliding window slope calculation.
"""

from typing import List


def calculate_slope_window(pressures: List[float], timestamps: List[float]) -> float:
    """
    Calculate the average slope of four segments within a five-point sliding window.
    
    Args:
        pressures: List of 5 pressure values (raw sensor units)
        timestamps: Corresponding list of 5 timestamps (seconds)
    
    Returns:
        Average slope (pressure/second)
    
    Raises:
        ValueError: When input length is not exactly 5
    
    Algorithm:
        Uses a 5-point window to calculate slopes between consecutive points:
        slope = Σ(pᵢ₊₁ - pᵢ)/(tᵢ₊₁ - tᵢ) / 4
    """
    if len(pressures) != 5 or len(timestamps) != 5:
        raise ValueError("Exactly 5 points are required for slope calculation")
    
    slopes = []
    for i in range(1, 5):
        dt = timestamps[i] - timestamps[i-1]
        if dt <= 1e-6:
            dt = 1e-6
        slope = (pressures[i] - pressures[i-1]) / dt
        slopes.append(slope)
    
    return sum(slopes) / len(slopes)