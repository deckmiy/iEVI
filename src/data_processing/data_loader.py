"""
Data loader module for pressure data.
Handles loading pressure data from CSV files and other sources.
"""

import csv
from typing import List, Tuple, Optional


def load_pressure_data(
    csv_file: str,
    timestamp_column: Optional[int] = 0,
    pressure_column: Optional[int] = 1,
    has_header: bool = True,
    default_sample_rate: float = 1.0
) -> Tuple[List[float], List[float]]:
    """
    Load pressure data from a CSV file.
    
    Args:
        csv_file: Path to CSV file
        timestamp_column: Column index for timestamps (0-based), or None for auto-generated
        pressure_column: Column index for pressure values (0-based)
        has_header: Whether the CSV file has a header row
        default_sample_rate: Sample rate for auto-generated timestamps (Hz)
    
    Returns:
        Tuple of (timestamps, pressures)
    
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If no valid data is found or columns are invalid
    
    Notes:
        - If timestamp_column is None, timestamps are auto-generated starting from 0
        - Pressure column is required
    """
    timestamps = []
    pressures = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        if has_header:
            next(reader, None)  # Skip header
        
        for row_num, row in enumerate(reader, start=1):
            if not row:
                continue
            
            # Clean and validate row
            row = [cell.strip() for cell in row if cell.strip()]
            if not row:
                continue
            
            try:
                # Parse pressure value
                if pressure_column is None or pressure_column >= len(row):
                    raise ValueError(f"Pressure column {pressure_column} out of range")
                
                pressure = float(row[pressure_column])
                
                # Parse or generate timestamp
                if timestamp_column is None:
                    # Auto-generate timestamp based on sample rate
                    timestamp = len(pressures) / default_sample_rate
                elif timestamp_column < len(row):
                    timestamp = float(row[timestamp_column])
                else:
                    raise ValueError(f"Timestamp column {timestamp_column} out of range")
                
                timestamps.append(timestamp)
                pressures.append(pressure)
                
            except (ValueError, IndexError) as e:
                # Skip rows with parsing errors
                continue
    
    if not pressures:
        raise ValueError(f"No valid data found in {csv_file}")
    
    return timestamps, pressures


def load_csv_data_simple(csv_file: str) -> Tuple[List[float], List[float]]:
    """
    Simple CSV loader that auto-detects format.
    
    Args:
        csv_file: Path to CSV file
    
    Returns:
        Tuple of (timestamps, pressures)
    
    Detects format:
        1. Two columns: timestamp, pressure
        2. One column: pressure (auto-generates timestamps at 1Hz)
    """
    timestamps = []
    pressures = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Try to detect if there's a header
        try:
            first_row = next(reader)
            # Check if first value looks like a number
            float(first_row[0])
            # If it's a number, it's data, not header
            reader = csv.reader(f)
            # Reset file
            f.seek(0)
            has_header = False
        except (ValueError, StopIteration):
            has_header = True
        
        reader = csv.reader(f)
        if has_header:
            next(reader, None)  # Skip header
        
        for row_num, row in enumerate(reader, start=1):
            if not row:
                continue
            
            # Clean row
            row = [cell.strip() for cell in row if cell.strip()]
            
            if len(row) >= 2:
                # Two columns: timestamp, pressure
                try:
                    timestamp = float(row[0])
                    pressure = float(row[1])
                    timestamps.append(timestamp)
                    pressures.append(pressure)
                except ValueError:
                    continue
            elif len(row) == 1:
                # One column: pressure only
                try:
                    pressure = float(row[0])
                    # Auto-generate timestamp (1Hz starting from 0)
                    timestamps.append(len(pressures))
                    pressures.append(pressure)
                except ValueError:
                    continue
    
    if not pressures:
        raise ValueError(f"No valid data found in {csv_file}")
    
    return timestamps, pressures