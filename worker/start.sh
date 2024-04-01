#!/bin/bash
set -e

touch this_is_a_test.txt

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d "venv/bin" ]; then
    # If not, create a virtual environment
    python3 -m venv venv
fi
# Activate the virtual environment
source "./venv/bin/activate"
# Install Python requirements
pip install -r requirements.txt
# python -m spacy download en_core_web_sm
# Start Python script as a daemon

python -u "v1/main copy.py" > output.log