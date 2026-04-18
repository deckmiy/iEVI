"""
Command-line interface for the Adaptive Piston Algorithm.
Provides user-friendly access to pressure data analysis and clogging detection.
"""

import argparse
import sys
import os
from typing import List, Tuple

from ..config import Config, default_config
from ..core import (
    detect_triggers,
    calculate_backflush_duration,
    calculate_backflush_intervals
)
from ..data_processing import (
    load_csv_data_simple,
    simulate_pressure_data,
    save_results_to_csv
)



def analyze_pressure_data(
    timestamps: List[float],
    pressures: List[float],
    slope_threshold: float = 20.0,
    grace_period: float = 5.0,
    min_trigger_interval: float = 13.0,
    backflush_flow_ml_hr: float = 10.0,
    backflush_volume_ml: float = 0.1
) -> Tuple[List[Tuple[float, float, float, float, float]], float]:
    """
    Analyze pressure data and detect clogging triggers.
    
    Args:
        timestamps: List of timestamps (seconds)
        pressures: List of pressure values
        slope_threshold: Slope threshold for clogging detection
        grace_period: Grace period after start (seconds)
        min_trigger_interval: Minimum interval between triggers (seconds)
        backflush_flow_ml_hr: Backflush flow rate (ml/hr)
        backflush_volume_ml: Backflush volume (ml)
    
    Returns:
        Tuple of (results, backflush_duration)
    """
    # Detect trigger points
    triggers = detect_triggers(
        pressure_series=pressures,
        timestamp_series=timestamps,
        slope_threshold=slope_threshold,
        grace_period=grace_period,
        min_trigger_interval=min_trigger_interval
    )
    
    # Calculate backflush duration
    backflush_duration = calculate_backflush_duration(
        backflush_volume_ml,
        backflush_flow_ml_hr
    )
    
    # Calculate backflush intervals
    results = calculate_backflush_intervals(triggers, backflush_duration)
    
    return results, backflush_duration


def print_results(results: List[Tuple[float, float, float, float, float]], 
                  backflush_duration: float):
    """Print analysis results to console."""
    if not results:
        print("\nNo trigger points detected.")
        return
    
    print(f"\nDetected {len(results)} trigger point(s):")
    print("=" * 80)
    
    for i, (trigger_time, trigger_idx, avg_slope, start_time, end_time) in enumerate(results):
        print(f"Trigger #{i+1}:")
        print(f"  Trigger Time: {trigger_time:.2f} s")
        print(f"  Data Index: {trigger_idx}")
        print(f"  Average Slope: {avg_slope:.2f} pressure/s")
        print(f"  Backflush Interval: [{start_time:.2f}, {end_time:.2f}] s")
        print(f"  Backflush Duration: {backflush_duration:.2f} s")
        print()


def create_argument_parser():
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Adaptive Piston Algorithm - Pressure Trigger Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Use simulated data
  %(prog)s --csv pressure_data.csv  # Load data from CSV file
  %(prog)s --csv data.csv --threshold 25 --grace 3 --interval 15
  %(prog)s --csv data.csv --flow 12 --volume 0.15
  %(prog)s --help                   # Show this help message
        """
    )
    
    # Data source arguments
    data_group = parser.add_argument_group('Data Source')
    data_group.add_argument(
        '--csv',
        type=str,
        help='CSV file containing pressure data'
    )
    data_group.add_argument(
        '--duration',
        type=float,
        default=120.0,
        help='Duration for simulated data (seconds, default: 120)'
    )
    
    # Configuration file
    config_group = parser.add_argument_group('Configuration')
    config_group.add_argument(
        '--config',
        type=str,
        help='JSON configuration file (overrides other parameters)'
    )
    config_group.add_argument(
        '--save-config',
        type=str,
        help='Save current parameters to JSON configuration file'
    )
    
    # Detection parameters
    detect_group = parser.add_argument_group('Detection Parameters')
    detect_group.add_argument(
        '--threshold',
        type=float,
        default=20.0,
        help='Slope threshold for clogging detection (pressure/s, default: 20.0)'
    )
    detect_group.add_argument(
        '--grace',
        type=float,
        default=5.0,
        help='Grace period after start (seconds, default: 5.0)'
    )
    detect_group.add_argument(
        '--interval',
        type=float,
        default=13.0,
        help='Minimum interval between triggers (seconds, default: 13.0)'
    )
    detect_group.add_argument(
        '--window',
        type=int,
        default=5,
        help='Sliding window size (default: 5)'
    )
    
    # Backflush parameters
    backflush_group = parser.add_argument_group('Backflush Parameters')
    backflush_group.add_argument(
        '--flow',
        type=float,
        default=10.0,
        help='Backflush flow rate (ml/hr, default: 10.0)'
    )
    backflush_group.add_argument(
        '--volume',
        type=float,
        default=0.1,
        help='Backflush volume (ml, default: 0.1)'
    )
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument(
        '--output',
        type=str,
        default='trigger_results.csv',
        help='Output CSV file (default: trigger_results.csv)'
    )

    output_group.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress console output'
    )
    
    return parser


def main():
    """Main entry point for CLI."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Load configuration from file if specified
    if args.config:
        if not args.quiet:
            print(f"Loading configuration from: {args.config}")
        try:
            config = Config.load_from_json(args.config)
            if not args.quiet:
                print("Configuration loaded successfully")
        except Exception as e:
            print(f"Error loading configuration file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        config = default_config
    
    # Override config with command-line arguments
    updates = {}
    # Hardcoded defaults from create_argument_parser
    default_threshold = 20.0
    default_grace = 5.0
    default_interval = 13.0
    default_flow = 10.0
    default_volume = 0.1
    default_duration = 120.0
    
    if args.threshold != default_threshold:
        updates['slope_threshold'] = args.threshold
    if args.grace != default_grace:
        updates['grace_period'] = args.grace
    if args.interval != default_interval:
        updates['min_trigger_interval'] = args.interval
    if args.flow != default_flow:
        updates['backflush_flow_ml_hr'] = args.flow
    if args.volume != default_volume:
        updates['backflush_volume_ml'] = args.volume
    if args.duration != default_duration:
        updates['simulation_duration'] = args.duration
    if args.quiet:
        updates['quiet_mode'] = args.quiet
    
    if updates:
        config.update_from_dict(updates)
        if not config.quiet_mode and args.config:
            print("Command-line parameters overriding configuration file")
    
    # Save configuration if requested
    if args.save_config:
        try:
            config.save_to_json(args.save_config)
            if not args.quiet:
                print(f"Configuration saved to: {args.save_config}")
        except Exception as e:
            print(f"Error saving configuration: {e}", file=sys.stderr)
            sys.exit(1)
        # Exit after saving config
        return 0
    
    # Print header (unless quiet mode)
    if not config.quiet_mode:
        print("Adaptive Piston Algorithm - Pressure Trigger Analysis")
        print("=" * 60)
        print(f"Slope Threshold: {config.slope_threshold} pressure/s")
        print(f"Grace Period: {config.grace_period} s")
        print(f"Minimum Trigger Interval: {config.min_trigger_interval} s")
        print(f"Backflush Flow Rate: {config.backflush_flow_ml_hr} ml/hr")
        print(f"Backflush Volume: {config.backflush_volume_ml} ml")
        print(f"Backflush Duration: {config.backflush_duration:.2f} s")
    
    # Load data
    if args.csv:
        if not config.quiet_mode:
            print(f"\nLoading data from CSV file: {args.csv}")
        try:
            timestamps, pressures = load_csv_data_simple(args.csv)
        except Exception as e:
            print(f"Error loading CSV file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if not config.quiet_mode:
            print("\nUsing simulated data (no CSV file provided)")
        timestamps, pressures = simulate_pressure_data(
            duration=config.simulation_duration,
            sample_rate=config.simulation_sample_rate,
            baseline=config.simulation_baseline_pressure,
            noise_std=config.simulation_noise_std,
            clog_events=config.simulation_clog_events
        )
    
    if not config.quiet_mode:
        print(f"Loaded {len(pressures)} data points")
        print(f"Time range: {timestamps[0]:.2f} - {timestamps[-1]:.2f} s")
        print(f"Pressure range: {min(pressures):.2f} - {max(pressures):.2f}")
    
    # Analyze data
    if not config.quiet_mode:
        print("\nAnalyzing data...")
    
    results, backflush_duration = analyze_pressure_data(
        timestamps=timestamps,
        pressures=pressures,
        slope_threshold=config.slope_threshold,
        grace_period=config.grace_period,
        min_trigger_interval=config.min_trigger_interval,
        backflush_flow_ml_hr=config.backflush_flow_ml_hr,
        backflush_volume_ml=config.backflush_volume_ml
    )
    
    # Print results
    if not config.quiet_mode:
        print_results(results, backflush_duration)
    
    # Save results to CSV
    default_output = 'trigger_results.csv'
    output_file = args.output if args.output != default_output else config.default_output_csv
    try:
        save_results_to_csv(results, output_file)
        if not config.quiet_mode:
            print(f"Results saved to: {output_file}")
    except Exception as e:
        print(f"Error saving results to CSV: {e}", file=sys.stderr)
    

    
    if not config.quiet_mode:
        print("\nAnalysis complete!")
    
    # Return exit code based on whether triggers were detected
    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())