#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define the base directory
BASE_DIR=$(pwd)
RAG_SUMMARIZER_DIR="$BASE_DIR/RAG_summarizer"

# Define paths to the Python scripts
SECTION_BUILDER_SCRIPT="$RAG_SUMMARIZER_DIR/section_builder.py"
UPSERT_AND_QUERY_SCRIPT="$RAG_SUMMARIZER_DIR/upsert_and_query.py"
SUMMARIZER_SCRIPT="$RAG_SUMMARIZER_DIR/summarizer.py"

# Define the log file
LOG_FILE="$BASE_DIR/run_rag_summarizer.log"

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
run_script "$SECTION_BUILDER_SCRIPT"
run_script "$UPSERT_AND_QUERY_SCRIPT"
run_script "$SUMMARIZER_SCRIPT"

# End logging
echo "Script execution completed at: $(date)" >> "$LOG_FILE"

# Notify completion
echo "All RAG summarizer scripts executed successfully. Logs can be found in $LOG_FILE."
