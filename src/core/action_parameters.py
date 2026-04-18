"""
Action parameter calculation for backflush operations.
Computes backflush duration based on volume and flow rate.
"""

def calculate_backflush_duration(
    backflush_volume_ml: float,
    backflush_flow_ml_hr: float
) -> float:
    """
    Calculate backflush duration based on volume and flow rate.
    
    Args:
        backflush_volume_ml: Backflush volume in milliliters
        backflush_flow_ml_hr: Backflush flow rate in milliliters per hour
    
    Returns:
        Backflush duration in seconds
    
    Formula:
        duration_seconds = (volume_ml / flow_ml_hr) × 3600
    
    Notes:
        Returns 0.0 if flow rate is too small (≤ 1e-6)
    """
    if backflush_flow_ml_hr <= 1e-6:
        return 0.0
    
    duration_hr = backflush_volume_ml / backflush_flow_ml_hr
    return duration_hr * 3600.0