"""
Advanced usage example for the Adaptive Piston Algorithm.
Demonstrates parameter sensitivity analysis, batch processing,
and real-time monitoring simulation.
"""

import argparse
import csv
import os
import random
import sys
from typing import List, Tuple

# Add project root to Python path when running this file directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core import (
    calculate_backflush_duration,
    calculate_backflush_intervals,
    detect_triggers,
)
from src.data_processing import save_analysis_summary, save_results_to_csv, simulate_pressure_data
from src.visualization import (
    ensure_dir,
    plot_pressure_analysis,
    plot_sensitivity_results,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the advanced example."""
    parser = argparse.ArgumentParser(
        description="Advanced example for Adaptive Piston Algorithm"
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Output directory for tables and figures (default: current directory)",
    )
    return parser.parse_args()


def load_custom_csv(filepath: str) -> Tuple[List[float], List[float]]:
    """
    Example of custom CSV loader with specific format.

    Expected format:
        Time (s), Pressure (units), Temperature (°C), Flow Rate (ml/hr)
    The algorithm only needs Time and Pressure columns.
    """
    timestamps = []
    pressures = []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header

        for row in reader:
            if len(row) >= 2:
                try:
                    timestamp = float(row[0])
                    pressure = float(row[1])
                    timestamps.append(timestamp)
                    pressures.append(pressure)
                except ValueError:
                    continue

    return timestamps, pressures


def parameter_sensitivity_analysis(
    timestamps: List[float],
    pressures: List[float],
    threshold_range: List[float],
    grace_range: List[float],
    min_trigger_interval: float = 13.0,
) -> List[dict]:
    """
    Perform sensitivity analysis by varying detection parameters.

    Returns a list of trigger-count results for each parameter combination.
    This function reports sensitivity only; it does not choose or label any
    parameter set as best.
    """
    results = []

    for threshold in threshold_range:
        for grace in grace_range:
            triggers = detect_triggers(
                pressure_series=pressures,
                timestamp_series=timestamps,
                slope_threshold=threshold,
                grace_period=grace,
                min_trigger_interval=min_trigger_interval,
            )

            results.append({
                "threshold": threshold,
                "grace_period": grace,
                "trigger_count": len(triggers),
                "trigger_times": [t[0] for t in triggers],
                "average_slopes": [t[2] for t in triggers] if triggers else [],
            })

    return results


def batch_analyze_files(
    filepaths: List[str],
    slope_threshold: float = 20.0,
    grace_period: float = 5.0,
    output_dir: str = "batch_results",
) -> dict:
    """Batch analyze multiple pressure data files."""
    os.makedirs(output_dir, exist_ok=True)

    summary = {
        "total_files": len(filepaths),
        "processed_files": 0,
        "total_triggers": 0,
        "file_results": [],
    }

    for filepath in filepaths:
        try:
            timestamps, pressures = load_custom_csv(filepath)
            triggers = detect_triggers(
                pressure_series=pressures,
                timestamp_series=timestamps,
                slope_threshold=slope_threshold,
                grace_period=grace_period,
            )
            backflush_duration = calculate_backflush_duration(0.1, 10.0)
            results = calculate_backflush_intervals(triggers, backflush_duration)

            filename = os.path.basename(filepath)
            output_file = os.path.join(output_dir, f"results_{filename}")
            save_results_to_csv(results, output_file)

            file_result = {
                "filename": filename,
                "data_points": len(pressures),
                "triggers": len(triggers),
                "first_trigger": triggers[0][0] if triggers else None,
                "max_slope": max([t[2] for t in triggers]) if triggers else 0.0,
            }
            summary["file_results"].append(file_result)
            summary["total_triggers"] += len(triggers)
            summary["processed_files"] += 1
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    return summary


def main() -> None:
    """Demonstrate advanced usage of the algorithm."""
    args = parse_args()
    output_dir = ensure_dir(args.output)
    figures_dir = ensure_dir(os.path.join(output_dir, "figures"))
    tables_dir = ensure_dir(os.path.join(output_dir, "tables"))

    print("Adaptive Piston Algorithm - Advanced Usage Example")
    print("=" * 60)

    # Example 1: Parameter sensitivity analysis.
    print("\n1. Parameter Sensitivity Analysis")
    print("-" * 40)

    random.seed(42)
    timestamps, pressures = simulate_pressure_data(
        duration=180.0,
        sample_rate=1.0,
        baseline=100.0,
        noise_std=2.0,
        clog_events=[
            (30.0, 8.0, 25.0),
            (75.0, 10.0, 30.0),
            (120.0, 6.0, 35.0),
            (150.0, 5.0, 40.0),
        ],
    )

    thresholds = [15.0, 20.0, 25.0, 30.0]
    grace_periods = [3.0, 5.0, 7.0]
    analysis_threshold = 20.0
    analysis_grace = 5.0
    analysis_min_interval = 13.0

    sensitivity_results = parameter_sensitivity_analysis(
        timestamps,
        pressures,
        thresholds,
        grace_periods,
        min_trigger_interval=analysis_min_interval,
    )

    print(f"   Tested {len(sensitivity_results)} parameter combinations")
    print("\n   Results summary:")
    print("   " + "-" * 35)
    print("   Threshold | Grace Period | Triggers")
    print("   " + "-" * 35)

    for result in sensitivity_results:
        print(
            f"   {result['threshold']:9.1f} | {result['grace_period']:12.1f} | "
            f"{result['trigger_count']:8d}"
        )

    sensitivity_plot = plot_sensitivity_results(
        sensitivity_results=sensitivity_results,
        output_file=os.path.join(figures_dir, "advanced_parameter_sensitivity.png"),
    )
    print(f"\n   Sensitivity plot saved: {sensitivity_plot}")

    # Example 2: Fixed-parameter analysis summary (table only, no duplicate plots).
    print("\n2. Fixed-Parameter Analysis Summary")
    print("-" * 40)
    print(
        "   Using fixed demonstration parameters: "
        f"threshold={analysis_threshold}, grace={analysis_grace}, "
        f"min_interval={analysis_min_interval}"
    )

    triggers = detect_triggers(
        pressure_series=pressures,
        timestamp_series=timestamps,
        slope_threshold=analysis_threshold,
        grace_period=analysis_grace,
        min_trigger_interval=analysis_min_interval,
    )

    backflush_duration = calculate_backflush_duration(0.1, 10.0)
    results = calculate_backflush_intervals(triggers, backflush_duration)
    results_csv = os.path.join(tables_dir, "advanced_trigger_results.csv")
    save_results_to_csv(results, results_csv)

    print(f"   Detected {len(triggers)} trigger point(s)")
    print(f"   Trigger result table saved: {results_csv}")

    # Example 3: Batch processing simulation.
    print("\n3. Batch Processing Simulation")
    print("-" * 40)
    print("   Simulating batch analysis with fixed demonstration parameters...")

    batch_summary = {
        "total_files": 5,
        "processed_files": 5,
        "total_triggers": 0,
        "file_results": [],
    }

    for i in range(1, 6):
        sim_timestamps, sim_pressures = simulate_pressure_data(
            duration=100.0 + i * 20,
            baseline=90.0 + i * 5,
            clog_events=[
                (20.0 + i * 5, 5.0 + i, 25.0 + i * 3),
            ],
        )

        sim_triggers = detect_triggers(
            pressure_series=sim_pressures,
            timestamp_series=sim_timestamps,
            slope_threshold=analysis_threshold,
            grace_period=analysis_grace,
            min_trigger_interval=analysis_min_interval,
        )

        batch_summary["file_results"].append({
            "filename": f"simulation_{i}.csv",
            "data_points": len(sim_pressures),
            "triggers": len(sim_triggers),
            "first_trigger": sim_triggers[0][0] if sim_triggers else None,
            "max_slope": max([t[2] for t in sim_triggers]) if sim_triggers else 0.0,
        })
        batch_summary["total_triggers"] += len(sim_triggers)

    print(f"   Processed {batch_summary['processed_files']} files")
    print(f"   Total triggers detected: {batch_summary['total_triggers']}")
    print(
        "   Average triggers per file: "
        f"{batch_summary['total_triggers'] / batch_summary['processed_files']:.1f}"
    )

    parameters = {
        "slope_threshold": analysis_threshold,
        "grace_period": analysis_grace,
        "min_trigger_interval": analysis_min_interval,
        "backflush_flow_ml_hr": 10.0,
        "backflush_volume_ml": 0.1,
        "backflush_duration_s": backflush_duration,
    }

    summary_csv = os.path.join(tables_dir, "advanced_analysis_summary.csv")
    try:
        save_analysis_summary(
            triggers=triggers,
            backflush_duration=backflush_duration,
            parameters=parameters,
            output_file=summary_csv,
        )
        print(f"   Analysis summary saved: {summary_csv}")
    except Exception as e:
        print(f"   Error saving summary: {e}")

    # Example 4: Real-time monitoring simulation.
    print("\n4. Real-time Monitoring Simulation")
    print("-" * 40)
    print("   Simulating real-time pressure monitoring...")
    print("   (This would connect to hardware sensors in a real application)")

    chunk_size = 50
    real_time_triggers = []

    for chunk_start in range(0, len(pressures), chunk_size):
        chunk_end = min(chunk_start + chunk_size, len(pressures))
        chunk_pressures = pressures[chunk_start:chunk_end]
        chunk_timestamps = timestamps[chunk_start:chunk_end]
        chunk_grace_period = analysis_grace if chunk_start == 0 else 0.0

        if chunk_start > 0:
            time_offset = timestamps[chunk_start]
            chunk_timestamps = [t - time_offset for t in chunk_timestamps]

        chunk_triggers = detect_triggers(
            pressure_series=chunk_pressures,
            timestamp_series=chunk_timestamps,
            slope_threshold=analysis_threshold,
            grace_period=chunk_grace_period,
            min_trigger_interval=analysis_min_interval,
        )

        if chunk_start > 0 and chunk_triggers:
            adjusted_triggers = []
            for trigger_time, trigger_idx, avg_slope in chunk_triggers:
                adjusted_time = trigger_time + timestamps[chunk_start]
                adjusted_idx = trigger_idx + chunk_start
                adjusted_triggers.append((adjusted_time, adjusted_idx, avg_slope))
            real_time_triggers.extend(adjusted_triggers)
        else:
            real_time_triggers.extend(chunk_triggers)

        if chunk_triggers:
            print(
                f"   Chunk {chunk_start // chunk_size + 1}: "
                f"Detected {len(chunk_triggers)} trigger(s) "
                f"(chunk grace={chunk_grace_period:.1f}s)"
            )

    real_time_results = calculate_backflush_intervals(real_time_triggers, backflush_duration)
    real_time_plot = plot_pressure_analysis(
        timestamps=timestamps,
        pressures=pressures,
        results=real_time_results,
        output_file=os.path.join(figures_dir, "advanced_realtime_triggers.png"),
        title="Advanced example: simulated real-time trigger detection",
    )

    print(f"\n   Total real-time triggers: {len(real_time_triggers)}")
    if real_time_triggers:
        print(f"   First trigger at: {real_time_triggers[0][0]:.1f}s")
        print(f"   Last trigger at: {real_time_triggers[-1][0]:.1f}s")
    print(f"   Real-time trigger plot saved: {real_time_plot}")

    print("\n" + "=" * 60)
    print("ADVANCED EXAMPLE COMPLETE")
    print("=" * 60)
    print("\nThis example demonstrated:")
    print("1. Parameter sensitivity analysis")
    print("2. Fixed-parameter analysis summary table")
    print("3. Batch processing simulation")
    print("4. Real-time monitoring concepts")
    print("\nThe actual hardware integration would be in the non-public layer.")


if __name__ == "__main__":
    main()
