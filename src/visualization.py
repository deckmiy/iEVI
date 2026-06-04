"""
Visualization helpers for the Adaptive Piston Algorithm.
Generates process-oriented figures for pressure traces, slope traces,
trigger points, backflush windows, and parameter sensitivity results.
"""

import os
from typing import Dict, Iterable, List, Sequence, Tuple


def ensure_dir(path: str) -> str:
    """Create a directory if needed and return the normalized path."""
    os.makedirs(path, exist_ok=True)
    return path


def resolve_output_csv_path(output_path: str, default_filename: str = "trigger_results.csv") -> str:
    """
    Resolve an output argument into a concrete CSV file path.

    The CLI historically received values such as ``--output /results``.
    Because ``/results`` is a directory, not a CSV file, this helper maps it to
    ``/results/trigger_results.csv`` instead of trying to write to a directory.
    """
    if not output_path:
        output_path = default_filename

    looks_like_directory = (
        output_path.endswith(os.sep)
        or os.path.isdir(output_path)
        or os.path.splitext(output_path)[1].lower() != ".csv"
    )

    if looks_like_directory:
        ensure_dir(output_path)
        output_path = os.path.join(output_path, default_filename)
    else:
        parent = os.path.dirname(output_path)
        if parent:
            ensure_dir(parent)

    return output_path


def calculate_sliding_slopes(
    timestamps: Sequence[float],
    pressures: Sequence[float],
    window_size: int = 5,
) -> Tuple[List[float], List[float]]:
    """
    Calculate average slopes for a sliding window.

    Returns slope timestamps aligned to the last timestamp in each window.
    """
    if len(timestamps) != len(pressures):
        raise ValueError("timestamps and pressures must have the same length")
    if window_size < 2:
        raise ValueError("window_size must be at least 2")
    if len(timestamps) < window_size:
        return [], []

    slope_times: List[float] = []
    slopes: List[float] = []

    for end_idx in range(window_size - 1, len(timestamps)):
        start_idx = end_idx - window_size + 1
        window_t = timestamps[start_idx:end_idx + 1]
        window_p = pressures[start_idx:end_idx + 1]

        segment_slopes = []
        for i in range(1, len(window_t)):
            dt = window_t[i] - window_t[i - 1]
            if dt <= 1e-6:
                dt = 1e-6
            segment_slopes.append((window_p[i] - window_p[i - 1]) / dt)

        slope_times.append(window_t[-1])
        slopes.append(sum(segment_slopes) / len(segment_slopes))

    return slope_times, slopes


def _prepare_matplotlib():
    """Import matplotlib with a non-interactive backend for batch runs."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def plot_pressure_analysis(
    timestamps: Sequence[float],
    pressures: Sequence[float],
    results: Sequence[Tuple[float, float, float, float, float]],
    output_file: str,
    title: str = "Pressure trace with triggers and backflush windows",
) -> str:
    """Plot pressure trace, trigger points, and backflush intervals."""
    plt = _prepare_matplotlib()
    parent = os.path.dirname(output_file)
    if parent:
        ensure_dir(parent)

    trigger_times = [row[0] for row in results]
    trigger_pressures = []
    for trigger_time in trigger_times:
        nearest_idx = min(range(len(timestamps)), key=lambda i: abs(timestamps[i] - trigger_time))
        trigger_pressures.append(pressures[nearest_idx])

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(timestamps, pressures, label="Pressure")

    for _, _, _, start_time, end_time in results:
        ax.axvspan(start_time, end_time, alpha=0.15)

    if trigger_times:
        ax.scatter(trigger_times, trigger_pressures, marker="o", label="Trigger points")
        for trigger_time in trigger_times:
            ax.axvline(trigger_time, linestyle="--", linewidth=1, alpha=0.5)

    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Pressure")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_file, dpi=150)
    plt.close(fig)
    return output_file


def plot_slope_analysis(
    timestamps: Sequence[float],
    pressures: Sequence[float],
    slope_threshold: float,
    trigger_times: Iterable[float],
    output_file: str,
    grace_period: float = 0.0,
    window_size: int = 5,
    title: str = "Sliding-window slope analysis",
) -> str:
    """Plot the sliding-window slope trace and the trigger threshold."""
    plt = _prepare_matplotlib()
    parent = os.path.dirname(output_file)
    if parent:
        ensure_dir(parent)

    slope_times, slopes = calculate_sliding_slopes(timestamps, pressures, window_size=window_size)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(slope_times, slopes, label="Average slope")
    ax.axhline(slope_threshold, linestyle="--", linewidth=1.2, label="Slope threshold")

    if grace_period > 0:
        ax.axvspan(0, grace_period, alpha=0.12, label="Grace period")

    for trigger_time in trigger_times:
        ax.axvline(trigger_time, linestyle=":", linewidth=1, alpha=0.6)

    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Average slope (pressure/s)")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_file, dpi=150)
    plt.close(fig)
    return output_file


def plot_sensitivity_results(
    sensitivity_results: Sequence[Dict],
    output_file: str,
    title: str = "Parameter sensitivity: trigger count",
) -> str:
    """Plot trigger count as a threshold-by-grace-period heatmap."""
    plt = _prepare_matplotlib()
    parent = os.path.dirname(output_file)
    if parent:
        ensure_dir(parent)

    thresholds = sorted({float(row["threshold"]) for row in sensitivity_results})
    grace_periods = sorted({float(row["grace_period"]) for row in sensitivity_results})

    matrix = []
    for threshold in thresholds:
        row_values = []
        for grace_period in grace_periods:
            match = next(
                row for row in sensitivity_results
                if float(row["threshold"]) == threshold and float(row["grace_period"]) == grace_period
            )
            row_values.append(int(match["trigger_count"]))
        matrix.append(row_values)

    fig, ax = plt.subplots(figsize=(8, 5))
    image = ax.imshow(matrix, aspect="auto")
    fig.colorbar(image, ax=ax, label="Trigger count")

    ax.set_xticks(range(len(grace_periods)))
    ax.set_xticklabels([f"{value:g}" for value in grace_periods])
    ax.set_yticks(range(len(thresholds)))
    ax.set_yticklabels([f"{value:g}" for value in thresholds])

    for row_idx, row_values in enumerate(matrix):
        for col_idx, value in enumerate(row_values):
            ax.text(col_idx, row_idx, str(value), ha="center", va="center")

    ax.set_title(title)
    ax.set_xlabel("Grace period (s)")
    ax.set_ylabel("Slope threshold (pressure/s)")
    fig.tight_layout()
    fig.savefig(output_file, dpi=150)
    plt.close(fig)
    return output_file
