"""
Backflush interval calculation for adaptive piston algorithm.
Computes backflush intervals based on trigger points and backflush parameters.
"""

from typing import List, Tuple


def estimate_backflush_interval(
    trigger_time: float,
    backflush_duration: float
) -> Tuple[float, float]:
    """
    Estimate backflush interval based on trigger time and backflush duration.
    
    Args:
        trigger_time: Time when clogging was detected (seconds)
        backflush_duration: Duration of backflush operation (seconds)
    
    Returns:
        Tuple of (backflush_start_time, backflush_end_time)
    
    Note:
        The backflush starts immediately at the trigger time.
    """
    backflush_start = trigger_time
    backflush_end = trigger_time + backflush_duration
    return backflush_start, backflush_end


def calculate_backflush_intervals(
    triggers: List[Tuple[float, float, float]],
    backflush_duration: float
) -> List[Tuple[float, float, float, float, float]]:
    """
    Calculate backflush intervals for multiple trigger points.
    
    Args:
        triggers: List of trigger points, each as (trigger_time, trigger_index, average_slope)
        backflush_duration: Duration of backflush operation (seconds)
    
    Returns:
        List of results, each as (trigger_time, trigger_index, average_slope, 
                                  backflush_start, backflush_end)
    """
    results = []
    for trigger_time, trigger_idx, avg_slope in triggers:
        backflush_start, backflush_end = estimate_backflush_interval(
            trigger_time, backflush_duration
        )
        results.append((trigger_time, trigger_idx, avg_slope, backflush_start, backflush_end))
    
    return results