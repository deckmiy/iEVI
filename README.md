#  Algorithm

An intelligent algorithm for detecting clogging events in fluid delivery systems using pressure slope analysis and adaptive backflush control.

## Overview

The Algorithm monitors pressure signals in real-time to detect clogging events in fluid delivery systems. When a clog is detected, the algorithm automatically triggers a backflush operation to clear the obstruction and resume normal operation.

### Key Features

- **Real-time pressure monitoring** with configurable sampling
- **Five-point sliding window** slope calculation
- **trigger detection** with grace period and minimum interval constraints
- **Configurable backflush parameters** (volume, flow rate, duration)
- **Modular architecture** separating core algorithms from hardware control

## Project Structure

```
adaptive-piston-algorithm/
├── README.md                          # This file
├── analyze_pressure.py                # Main entry point script
├── requirements.txt                   # Python dependencies
├── src/                               # Core source code
│   ├── __init__.py
│   ├── core/                          # Core algorithm modules
│   │   ├── __init__.py
│   │   ├── slope_calculation.py      # 5-point sliding window slope calculation
│   │   ├── trigger_detection.py      # Trigger detection logic
│   │   ├── action_parameters.py      # Backflush parameter calculation
│   │   └── backflush_calculation.py  # Backflush interval calculation
│   ├── data_processing/              # Data handling modules
│   │   ├── __init__.py
│   │   ├── data_simulator.py         # Synthetic pressure data generation
│   │   ├── data_loader.py            # CSV data loading
│   │   └── csv_handler.py            # Result export
│   └── cli/                          # Command-line interface
│       ├── __init__.py
│       └── main.py                   # CLI implementation
├── examples/                          # Usage examples
│   ├── basic_usage.py                # Basic algorithm demonstration
│   ├── advanced_usage.py             # Advanced features demonstration
│   └── data/
│       └── example_pressure_data.csv # Sample pressure data
├── tests/                            # Unit tests (to be implemented)
    ├── __init__.py
    ├── test_core.py
    ├── test_data_processing.py
    └── test_cli.py

```

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Quick Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/adaptive-piston-algorithm.git
cd adaptive-piston-algorithm

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

The core algorithm requires only Python standard libraries. Optional dependencies include:

- `numpy` (for advanced analysis): `pip install numpy`

## Quick Start

### Using the Command Line Interface

The easiest way to use the algorithm is through the command-line interface:

```bash
# Analyze simulated data with default parameters
python analyze_pressure.py

# Analyze data from a CSV file
python analyze_pressure.py --csv examples/data/example_pressure_data.csv

# Customize detection parameters
python analyze_pressure.py --threshold 25 --grace 3 --interval 15

# Specify backflush parameters
python analyze_pressure.py --flow 12 --volume 0.15
```

### Command Line Options

```
Data Source:
  --csv CSV             CSV file containing pressure data
  --duration DURATION   Duration for simulated data (seconds, default: 120)

Detection Parameters:
  --threshold THRESHOLD Slope threshold for clogging detection (pressure/s, default: 20.0)
  --grace GRACE         Grace period after start (seconds, default: 5.0)
  --interval INTERVAL   Minimum interval between triggers (seconds, default: 13.0)
  --window WINDOW       Sliding window size (default: 5)

Backflush Parameters:
  --flow FLOW           Backflush flow rate (ml/hr, default: 10.0)
  --volume VOLUME       Backflush volume (ml, default: 0.1)

Output Options:
  --output OUTPUT       Output CSV file (default: trigger_results.csv)
  --quiet               Suppress console output
```

### Basic Python Usage

```python
import sys
sys.path.insert(0, 'path/to/adaptive-piston-algorithm/src')

from core import detect_triggers, calculate_backflush_duration
from data_processing import simulate_pressure_data

# Generate simulated pressure data
timestamps, pressures = simulate_pressure_data(
    duration=120.0,
    sample_rate=1.0,
    baseline=100.0,
    noise_std=1.5,
    clog_events=[(25.0, 6.0, 35.0), (55.0, 7.0, 28.0)]
)

# Detect clogging triggers
triggers = detect_triggers(
    pressure_series=pressures,
    timestamp_series=timestamps,
    slope_threshold=20.0,
    grace_period=5.0,
    min_trigger_interval=13.0
)

# Calculate backflush duration
backflush_duration = calculate_backflush_duration(
    backflush_volume_ml=0.1,
    backflush_flow_ml_hr=10.0
)

print(f"Detected {len(triggers)} trigger(s)")
print(f"Backflush duration: {backflush_duration:.2f} seconds")
```

## Core Algorithm

### Slope Calculation

The algorithm uses a five-point sliding window to calculate the average slope of pressure changes:

```
slope = Σ(pᵢ₊₁ - pᵢ)/(tᵢ₊₁ - tᵢ) / 4
```

Where:
- `pᵢ` is the pressure at point i
- `tᵢ` is the timestamp at point i
- The sum is over the 4 segments in a 5-point window

### Trigger Detection Logic

1. **Grace Period**: No detection for the first N seconds after startup
2. **Sliding Window**: Maintains the last 5 pressure points
3. **Threshold Comparison**: Compares calculated slope against threshold
4. **Minimum Interval**: Enforces minimum time between consecutive triggers


## Examples

### Example 1: Basic Analysis

```bash
python analyze_pressure.py --csv data.csv --output results.csv
```

This loads pressure data from `data.csv`, analyzes it with default parameters, and saves results to `results.csv`.

### Example 2: Parameter Tuning

```bash
python analyze_pressure.py --threshold 15 --grace 2 --interval 10
```

This uses more sensitive detection parameters (lower threshold, shorter grace period and interval).

### Example 3: Batch Processing

```python
# Example of batch processing multiple files
from data_processing.data_loader import load_csv_data_simple
from core import detect_triggers

files = ['data1.csv', 'data2.csv', 'data3.csv']
results = {}

for file in files:
    timestamps, pressures = load_csv_data_simple(file)
    triggers = detect_triggers(pressures, timestamps)
    results[file] = len(triggers)

print("Batch analysis complete:", results)
```

## Data Format

### CSV Format

The algorithm supports two CSV formats:

1. **Two columns**: timestamp (seconds), pressure (units)
   ```
   0.0,100.2
   1.0,101.5
   2.0,102.8
   ```

2. **Single column**: pressure only (timestamps auto-generated at 1Hz)
   ```
   100.2
   101.5
   102.8
   ```

### Synthetic Data Generation

For testing and demonstration, synthetic pressure data can be generated:

```python
from data_processing import simulate_pressure_data

timestamps, pressures = simulate_pressure_data(
    duration=120.0,          # 120 seconds of data
    sample_rate=1.0,         # 1 sample per second
    baseline=100.0,          # Baseline pressure
    noise_std=1.5,           # Gaussian noise standard deviation
    clog_events=[            # Simulated clogging events
        (25.0, 6.0, 35.0),   # Start at 25s, duration 6s, slope 35
        (55.0, 7.0, 28.0)    # Start at 55s, duration 7s, slope 28
    ]
)
```



## API Reference

### Core Modules

#### `core.slope_calculation`
- `calculate_slope_window(pressures, timestamps)`: Calculate average slope from 5-point window

#### `core.trigger_detection`
- `detect_triggers(pressure_series, timestamp_series, ...)`: Detect clogging triggers

#### `core.action_parameters`
- `calculate_backflush_duration(volume_ml, flow_ml_hr)`: Calculate backflush duration

#### `core.backflush_calculation`
- `estimate_backflush_interval(trigger_time, duration)`: Estimate backflush interval
- `calculate_backflush_intervals(triggers, duration)`: Calculate intervals for multiple triggers

### Data Processing Modules

#### `data_processing.data_simulator`
- `simulate_pressure_data(...)`: Generate synthetic pressure data

#### `data_processing.data_loader`
- `load_pressure_data(csv_file, ...)`: Load pressure data from CSV
- `load_csv_data_simple(csv_file)`: Simple CSV loader with auto-format detection

#### `data_processing.csv_handler`
- `save_results_to_csv(results, output_file)`: Save analysis results to CSV
- `save_analysis_summary(...)`: Save comprehensive analysis summary



## Testing

Run the example scripts to verify installation:

```bash
# Run basic usage example
python examples/basic_usage.py

# Run advanced usage example
python examples/advanced_usage.py

# Test command-line interface
python analyze_pressure.py
```

## Performance

The algorithm is designed for real-time operation with the following characteristics:

- **Low latency**: Process each sample in O(1) time
- **Memory efficient**: Maintains only a sliding window of recent samples
- **Configurable sensitivity**: Adjustable parameters for different applications
- **Robust to noise**: Uses multi-point averaging to reduce noise sensitivity

## License

This project is licensed for academic and research use. For commercial use, please contact the authors.

## Citation

If you use this algorithm in your research, please cite:

```
[Citation information to be added]
```

## Contact

For questions, issues, or collaborations, please contact:
- Research Team: research@pistonalgorithm.example.com
- Project Repository: https://github.com/yourusername/adaptive-piston-algorithm

## Acknowledgements

This research was supported by [Your Institution/Funding Source].

---

**Note**: This repository contains only the public layer of the algorithm. Hardware-specific implementations (serial communication, pump control, device protocols) are maintained separately.