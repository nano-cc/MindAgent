#!/bin/bash

# ChatMind Python Start Script

echo "================================"
echo "ChatMind Python"
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p data/documents
mkdir -p data/chroma
mkdir -p logs

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please configure your .env file before starting the application."
    exit 1
fi

# Start the application
echo "Starting ChatMind Python..."
echo ""
python -m app.main
