#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define the base directory
BASE_DIR=$(pwd)

# Define paths to the Python scripts
PREPROCESSING_SCRIPT="$BASE_DIR/preprocessing.py"
TOC_CLASSIFIER_SCRIPT="$BASE_DIR/toc_classifier.py"
TOC_MAPPER_SCRIPT="$BASE_DIR/toc_mapper.py"
CHUNK_EXTRACTOR_SCRIPT="$BASE_DIR/chunk_extractor.py"
CSV_BUILDER_SCRIPT="$BASE_DIR/csv_builder.py"
ANOMALIES_SCRIPT="$BASE_DIR/anomalies.py"

# Define the log file
LOG_FILE="$BASE_DIR/run_all.log"

# Function to run a Python script
run_script() {
    local script_path=$1
    echo "Running $script_path..."
    python "$script_path" >> "$LOG_FILE" 2>&1
    echo "Finished running $script_path"
}

# Start logging
echo "Script execution started at: $(date)" > "$LOG_FILE"

# Run each script
run_script "$PREPROCESSING_SCRIPT"
run_script "$TOC_CLASSIFIER_SCRIPT"
run_script "$TOC_MAPPER_SCRIPT"
run_script "$CHUNK_EXTRACTOR_SCRIPT"
run_script "$CSV_BUILDER_SCRIPT"
run_script "$ANOMALIES_SCRIPT"

# End logging
echo "Script execution completed at: $(date)" >> "$LOG_FILE"

# Notify completion
echo "All scripts executed successfully. Logs can be found in $LOG_FILE."
