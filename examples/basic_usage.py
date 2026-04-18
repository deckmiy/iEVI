"""
Basic usage example for the Adaptive Piston Algorithm.
Demonstrates core functionality with simulated data.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import Config, default_config
from src.core import (
    calculate_slope_window,
    detect_triggers,
    calculate_backflush_duration,
    calculate_backflush_intervals
)
from src.data_processing import simulate_pressure_data


def main():
    """Demonstrate basic usage of the algorithm with configuration system."""
    print("Adaptive Piston Algorithm - Basic Usage Example")
    print("=" * 60)
    
    # Step 1: Show configuration usage
    print("\n1. Configuration System")
    print("-" * 40)
    
    # Display default configuration
    print("   Default configuration:")
    print(f"   - Slope threshold: {default_config.slope_threshold} pressure/s")
    print(f"   - Grace period: {default_config.grace_period} s")
    print(f"   - Minimum trigger interval: {default_config.min_trigger_interval} s")
    print(f"   - Backflush volume: {default_config.backflush_volume_ml} ml")
    print(f"   - Backflush flow rate: {default_config.backflush_flow_ml_hr} ml/hr")
    print(f"   - Backflush duration: {default_config.backflush_duration:.2f} s")
    
    # Create a custom configuration
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
    
    # Step 2: Generate simulated pressure data using configuration
    print("\n2. Generating simulated pressure data...")
    timestamps, pressures = simulate_pressure_data(
        duration=custom_config.simulation_duration,
        sample_rate=custom_config.simulation_sample_rate,
        baseline=custom_config.simulation_baseline_pressure,
        noise_std=custom_config.simulation_noise_std,
        clog_events=custom_config.simulation_clog_events
    )
    
    print(f"   Generated {len(pressures)} data points")
    print(f"   Time range: {timestamps[0]:.1f} - {timestamps[-1]:.1f} s")
    print(f"   Pressure range: {min(pressures):.2f} - {max(pressures):.2f}")
    
    # Step 3: Calculate slope for a sample window
    print("\n3. Calculating slope for a sample window...")
    sample_window = pressures[20:25]  # Points 20-24
    sample_times = timestamps[20:25]
    slope = calculate_slope_window(sample_window, sample_times)
    print(f"   Sample window pressures: {sample_window}")
    print(f"   Sample window times: {sample_times}")
    print(f"   Calculated slope: {slope:.2f} pressure/s")
    
    # Step 4: Detect trigger points using configuration
    print("\n4. Detecting trigger points...")
    triggers = detect_triggers(
        pressure_series=pressures,
        timestamp_series=timestamps,
        slope_threshold=custom_config.slope_threshold,
        grace_period=custom_config.grace_period,
        min_trigger_interval=custom_config.min_trigger_interval
    )
    
    print(f"   Detected {len(triggers)} trigger point(s)")
    for i, (trigger_time, trigger_idx, avg_slope) in enumerate(triggers):
        print(f"   Trigger #{i+1}: Time={trigger_time:.1f}s, "
              f"Index={trigger_idx}, Slope={avg_slope:.2f}")
    
    # Step 5: Calculate backflush parameters using configuration
    print("\n5. Calculating backflush parameters...")
    backflush_duration = calculate_backflush_duration(
        custom_config.backflush_volume_ml,
        custom_config.backflush_flow_ml_hr
    )
    
    print(f"   Backflush flow rate: {custom_config.backflush_flow_ml_hr} ml/hr")
    print(f"   Backflush volume: {custom_config.backflush_volume_ml} ml")
    print(f"   Backflush duration: {backflush_duration:.2f} s")
    
    # Step 6: Calculate backflush intervals
    print("\n6. Calculating backflush intervals...")
    results = calculate_backflush_intervals(triggers, backflush_duration)
    
    print(f"   Calculated {len(results)} backflush interval(s)")
    for i, (trigger_time, trigger_idx, avg_slope, start_time, end_time) in enumerate(results):
        print(f"   Interval #{i+1}: [{start_time:.1f}, {end_time:.1f}] s")
    
    # Step 7: Save configuration to file
    print("\n7. Saving configuration to file...")
    try:
        config_file = "basic_example_config.json"
        custom_config.save_to_json(config_file)
        print(f"   Configuration saved to: {config_file}")
        print("   You can load this config with: --config basic_example_config.json")
    except Exception as e:
        print(f"   Error saving configuration: {e}")
    
    # Step 8: Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total data points: {len(pressures)}")
    print(f"Trigger points detected: {len(triggers)}")
    print(f"Backflush duration per trigger: {backflush_duration:.2f} s")
    
    if triggers:
        total_backflush_time = len(triggers) * backflush_duration
        total_time = timestamps[-1] - timestamps[0]
        print(f"Total backflush time: {total_backflush_time:.2f} s")
        print(f"Percentage of time in backflush: {(total_backflush_time / total_time * 100):.1f}%")
        print(f"Configuration file: basic_example_config.json")
    
    print("\nExample completed successfully!")
    print("\nKey improvements demonstrated:")
    print("1. Centralized configuration management")
    print("2. Configuration export/import via JSON files")


if __name__ == "__main__":
    main()