#!/bin/bash

# Run tests

echo "Running tests..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run tests
pytest

echo "Tests completed."
