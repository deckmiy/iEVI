"""
CSV handler module for saving analysis results.
Provides functions for exporting trigger results to CSV format.
"""

import csv
from typing import List, Tuple


def save_results_to_csv(
    results: List[Tuple[float, float, float, float, float]],
    output_file: str = "trigger_results.csv",
    include_duration: bool = True
) -> None:
    """
    Save trigger analysis results to a CSV file.
    
    Args:
        results: List of trigger results, each as (trigger_time, trigger_index, 
                 average_slope, backflush_start, backflush_end)
        output_file: Path to output CSV file
        include_duration: Whether to include backflush duration column
    
    Returns:
        None
    
    Example:
        >>> results = [(28.0, 28, 26.33, 28.0, 64.0), (58.0, 58, 21.73, 58.0, 94.0)]
        >>> save_results_to_csv(results, "results.csv")
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        header = [
            "Trigger Point",
            "Trigger Time (s)",
            "Data Index",
            "Average Slope (pressure/s)",
            "Backflush Start (s)",
            "Backflush End (s)"
        ]
        if include_duration:
            header.append("Backflush Duration (s)")
        
        writer.writerow(header)
        
        # Write data rows
        for i, (trigger_time, trigger_idx, avg_slope, start_time, end_time) in enumerate(results):
            row = [
                i + 1,
                f"{trigger_time:.2f}",
                trigger_idx,
                f"{avg_slope:.2f}",
                f"{start_time:.2f}",
                f"{end_time:.2f}"
            ]
            if include_duration:
                duration = end_time - start_time
                row.append(f"{duration:.2f}")
            
            writer.writerow(row)


def load_csv_data(
    csv_file: str,
    delimiter: str = ',',
    has_header: bool = True
) -> Tuple[List[List[str]], List[str]]:
    """
    Generic CSV loader that returns all data as strings.
    
    Args:
        csv_file: Path to CSV file
        delimiter: CSV delimiter character
        has_header: Whether CSV has a header row
    
    Returns:
        Tuple of (data_rows, header_row)
    
    Note:
        - Returns empty list for header if has_header is False
        - All values are returned as strings
    """
    data = []
    header = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=delimiter)
        
        if has_header:
            try:
                header = next(reader)
            except StopIteration:
                header = []
        
        for row in reader:
            if row:  # Skip empty rows
                data.append(row)
    
    return data, header


def save_analysis_summary(
    triggers: List[Tuple[float, float, float]],
    backflush_duration: float,
    parameters: dict,
    output_file: str = "analysis_summary.csv"
) -> None:
    """
    Save comprehensive analysis summary to CSV.
    
    Args:
        triggers: List of trigger points
        backflush_duration: Backflush duration (seconds)
        parameters: Dictionary of analysis parameters
        output_file: Path to output CSV file
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write parameters section
        writer.writerow(["Analysis Parameters"])
        writer.writerow(["Parameter", "Value"])
        for key, value in parameters.items():
            writer.writerow([key, str(value)])
        
        writer.writerow([])  # Empty row for separation
        
        # Write triggers section
        writer.writerow(["Trigger Points"])
        writer.writerow(["Trigger", "Time (s)", "Index", "Slope (pressure/s)"])
        for i, (trigger_time, trigger_idx, avg_slope) in enumerate(triggers):
            writer.writerow([i + 1, f"{trigger_time:.2f}", trigger_idx, f"{avg_slope:.2f}"])
        
        writer.writerow([])  # Empty row for separation
        
        # Write backflush info
        writer.writerow(["Backflush Information"])
        writer.writerow(["Parameter", "Value"])
        writer.writerow(["Backflush Duration (s)", f"{backflush_duration:.2f}"])
        writer.writerow(["Number of Triggers", len(triggers)])