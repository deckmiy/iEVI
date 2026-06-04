#!/usr/bin/env bash
# When you click "Reproducible Run", the code in this file will execute.

set -ex

RESULTS_DIR="${RESULTS_DIR:-/results}"
CODE_ISOLATION_DIR="${CODE_ISOLATION_DIR:-/code/code_isolation}"
CODE_PROFILING_DIR="${CODE_PROFILING_DIR:-/code/code_profiling}"

mkdir -p "$RESULTS_DIR"
rm -rf "$RESULTS_DIR/figures"
mkdir -p "$RESULTS_DIR/figures"
mkdir -p "$RESULTS_DIR/tables"
mkdir -p "$RESULTS_DIR/classification_results"

cd "$CODE_ISOLATION_DIR"
python -m src.cli.main \
  --output "$RESULTS_DIR/tables/trigger_results.csv" \
  --plot \
  --figures-dir "$RESULTS_DIR/figures"

python example/advanced_usage.py --output "$RESULTS_DIR"
python example/basic_usage.py --output "$RESULTS_DIR"

if [ -d "$CODE_PROFILING_DIR" ]; then
  cd "$CODE_PROFILING_DIR"
  ln -sfn /data data

  for script in \
    "ComBat1.R" \
    "Heatmap.R" \
    "LDA_visualization.R" \
    "PCA.R" \
    "PLS-DA.R" \
    "RF+NNET+LDA+Confusion_matrix+ROC+PR.R" \
    "Significance_heatmap.R" \
    "t_SNE_cell.R"; do
    if [ -f "$script" ]; then
      Rscript "$script"
    else
      echo "Skipping missing R script: $script"
    fi
  done
else
  echo "Skipping profiling scripts: $CODE_PROFILING_DIR not found"
fi