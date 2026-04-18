"""
Core algorithm modules for adaptive piston control.
Includes slope calculation, trigger detection, and action parameter calculation.
"""

from .slope_calculation import calculate_slope_window
from .trigger_detection import detect_triggers
from .action_parameters import calculate_backflush_duration
from .backflush_calculation import estimate_backflush_interval, calculate_backflush_intervals