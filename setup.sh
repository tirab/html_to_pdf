#!/bin/bash
# setup.sh: Create venv, install requirements, and run the app

set -e

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running the app..."
python main.py "$@"
