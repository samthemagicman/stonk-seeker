#!/bin/bash
if [ ! -d "venv" ] && [ ! -d "venv/bin" ]; then
    # If not, create a virtual environment
    python3 -m venv venv
fi
source "./venv/bin/activate"
pip install -r requirements.txt