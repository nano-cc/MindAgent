#!/bin/bash

# ChatMind Python Setup Script

echo "================================"
echo "ChatMind Python Setup"
echo "================================"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p data/documents
mkdir -p data/chroma
mkdir -p logs

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "================================"
    echo "Setup complete!"
    echo "================================"
    echo ""
    echo "IMPORTANT: Please configure your .env file:"
    echo "1. Edit .env with your API keys and database settings"
    echo "2. Ensure PostgreSQL database is created"
    echo "3. Run: alembic upgrade head  (to initialize database)"
    echo ""
    echo "Then start with: ./start.sh"
else
    echo "================================"
    echo "Setup complete!"
    echo "================================"
    echo ""
    echo "To start the application, run: ./start.sh"
fi
