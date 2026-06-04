"""
Basic usage example for the Adaptive Piston Algorithm.
Demonstrates core functionality with simulated data and saves tabular outputs.
"""

import argparse
import os
import sys
from typing import List, Tuple

# Add project root to Python path when running this file directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config import Config, default_config
from src.core import (
    calculate_backflush_duration,
    calculate_backflush_intervals,
    calculate_slope_window,
    detect_triggers,
)
from src.data_processing import save_results_to_csv, simulate_pressure_data
from src.visualization import ensure_dir


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the basic example."""
    parser = argparse.ArgumentParser(
        description="Basic example for Adaptive Piston Algorithm"
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Output directory for tables and figures (default: current directory)",
    )
    return parser.parse_args()


def merge_intervals(
    intervals: List[Tuple[float, float]],
    lower_bound: float,
    upper_bound: float,
) -> List[Tuple[float, float]]:
    """Merge overlapping intervals after clipping them to the analyzed time range."""
    clipped = []
    for start, end in intervals:
        start = max(start, lower_bound)
        end = min(end, upper_bound)
        if end > start:
            clipped.append((start, end))

    if not clipped:
        return []

    clipped.sort()
    merged = [clipped[0]]
    for start, end in clipped[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def main() -> None:
    """Demonstrate basic usage of the algorithm with configuration system."""
    args = parse_args()
    output_dir = ensure_dir(args.output)
    tables_dir = ensure_dir(os.path.join(output_dir, "tables"))

    print("Adaptive Piston Algorithm - Basic Usage Example")
    print("=" * 60)

    # Step 1: Show configuration usage.
    print("\n1. Configuration System")
    print("-" * 40)

    print("   Default configuration:")
    print(f"   - Slope threshold: {default_config.slope_threshold} pressure/s")
    print(f"   - Grace period: {default_config.grace_period} s")
    print(f"   - Minimum trigger interval: {default_config.min_trigger_interval} s")
    print(f"   - Backflush volume: {default_config.backflush_volume_ml} ml")
    print(f"   - Backflush flow rate: {default_config.backflush_flow_ml_hr} ml/hr")
    print(f"   - Backflush duration: {default_config.backflush_duration:.2f} s")

    print("\n   Creating custom configuration...")
    custom_config = Config(
        slope_threshold=18.0,
        grace_period=3.0,
        min_trigger_interval=10.0,
        backflush_volume_ml=0.15,
        backflush_flow_ml_hr=12.0,
        simulation_duration=100.0,
    )

    print("   Custom configuration created successfully")
    print(f"   - Updated slope threshold: {custom_config.slope_threshold} pressure/s")
    print(f"   - Updated backflush duration: {custom_config.backflush_duration:.2f} s")

    # Step 2: Generate simulated pressure data.
    print("\n2. Generating simulated pressure data...")
    timestamps, pressures = simulate_pressure_data(
        duration=custom_config.simulation_duration,
        sample_rate=custom_config.simulation_sample_rate,
        baseline=custom_config.simulation_baseline_pressure,
        noise_std=custom_config.simulation_noise_std,
        clog_events=custom_config.simulation_clog_events,
    )

    print(f"   Generated {len(pressures)} data points")
    print(f"   Time range: {timestamps[0]:.1f} - {timestamps[-1]:.1f} s")
    print(f"   Pressure range: {min(pressures):.2f} - {max(pressures):.2f}")

    # Step 3: Calculate slope for a sample window.
    print("\n3. Calculating slope for a sample window...")
    sample_window = pressures[20:25]
    sample_times = timestamps[20:25]
    slope = calculate_slope_window(sample_window, sample_times)
    print(f"   Sample window pressures: {sample_window}")
    print(f"   Sample window times: {sample_times}")
    print(f"   Calculated slope: {slope:.2f} pressure/s")

    # Step 4: Detect trigger points.
    print("\n4. Detecting trigger points...")
    triggers = detect_triggers(
        pressure_series=pressures,
        timestamp_series=timestamps,
        slope_threshold=custom_config.slope_threshold,
        grace_period=custom_config.grace_period,
        min_trigger_interval=custom_config.min_trigger_interval,
    )

    print(f"   Detected {len(triggers)} trigger point(s)")
    for i, (trigger_time, trigger_idx, avg_slope) in enumerate(triggers):
        print(
            f"   Trigger #{i + 1}: Time={trigger_time:.1f}s, "
            f"Index={trigger_idx}, Slope={avg_slope:.2f}"
        )

    # Step 5: Calculate backflush parameters.
    print("\n5. Calculating backflush parameters...")
    backflush_duration = calculate_backflush_duration(
        custom_config.backflush_volume_ml,
        custom_config.backflush_flow_ml_hr,
    )

    print(f"   Backflush flow rate: {custom_config.backflush_flow_ml_hr} ml/hr")
    print(f"   Backflush volume: {custom_config.backflush_volume_ml} ml")
    print(f"   Backflush duration: {backflush_duration:.2f} s")

    # Step 6: Calculate backflush intervals.
    print("\n6. Calculating backflush intervals...")
    results = calculate_backflush_intervals(triggers, backflush_duration)

    print(f"   Calculated {len(results)} backflush interval(s)")
    for i, (_, _, _, start_time, end_time) in enumerate(results):
        print(f"   Interval #{i + 1}: [{start_time:.1f}, {end_time:.1f}] s")

    result_csv = os.path.join(tables_dir, "basic_trigger_results.csv")
    save_results_to_csv(results, result_csv)
    print(f"   Trigger result table saved to: {result_csv}")

    # Step 7: Save configuration only (plots are intentionally omitted to avoid duplication).
    print("\n7. Saving configuration...")

    try:
        config_file = os.path.join(tables_dir, "basic_example_config.json")
        custom_config.save_to_json(config_file)
        print(f"   Configuration saved to: {config_file}")
        print(f"   You can load this config with: --config {config_file}")
    except Exception as e:
        print(f"   Error saving configuration: {e}")

    # Step 8: Summary.
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total data points: {len(pressures)}")
    print(f"Trigger points detected: {len(triggers)}")
    print(f"Backflush duration per trigger: {backflush_duration:.2f} s")

    if triggers:
        nominal_backflush_time = len(triggers) * backflush_duration
        total_time = timestamps[-1] - timestamps[0]
        merged = merge_intervals(
            [(row[3], row[4]) for row in results],
            lower_bound=timestamps[0],
            upper_bound=timestamps[-1],
        )
        effective_backflush_time = sum(end - start for start, end in merged)
        print(f"Nominal backflush time: {nominal_backflush_time:.2f} s")
        print(f"Effective backflush time within data range: {effective_backflush_time:.2f} s")
        print(
            "Effective percentage of analyzed time in backflush: "
            f"{(effective_backflush_time / total_time * 100):.1f}%"
        )

    print("\nExample completed successfully!")
    print("\nKey improvements demonstrated:")
    print("1. Centralized configuration management")
    print("2. Configuration export/import via JSON files")
    print("3. Trigger table export and configuration management")


if __name__ == "__main__":
    main()
