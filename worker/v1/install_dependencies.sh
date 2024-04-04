#!/bin/bash
set -e

if [ ! -d "venv" ] && [ ! -d "venv/bin" ]; then
    # If not, create a virtual environment
    python3 -m venv venv
fi
source "./venv/bin/activate"

pip install pika psycopg[binary] asyncpg praw diskcache spacy
python -m spacy download en_core_web_sm

# pip install -r requirements.txt