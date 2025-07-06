#!/bin/bash
# Helper script to run Python scripts with correct PYTHONPATH
# Usage: ./run_script.sh scripts/script_name.py [args...]

if [ $# -eq 0 ]; then
    echo "Usage: $0 <script_path> [args...]"
    echo "Example: $0 scripts/extract_pdf.py"
    exit 1
fi

SCRIPT_PATH="$1"
shift  # Remove the first argument, leaving any additional args

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Script not found: $SCRIPT_PATH"
    exit 1
fi

# Activate virtual environment if present
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Run the script with PYTHONPATH set to current directory
echo "🚀 Running $SCRIPT_PATH with PYTHONPATH=."
PYTHONPATH=. python "$SCRIPT_PATH" "$@"
