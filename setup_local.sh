#!/bin/bash

# Setup script for local execution with Ollama

# Step 1: Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping Python dependencies installation."
fi

# Step 2: Install Ollama
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Please install Ollama manually from https://ollama.ai."
else
    echo "Ollama is already installed."
fi

# Step 3: Verify local data files
DATA_FILES=("data/hevy_stats.csv" "data/Chat Memory.csv" "data/HEVY APP exercises.csv")
for file in "${DATA_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "Warning: Missing data file $file. Please add it to the data/ directory."
    else
        echo "Found $file."
    fi
done

# Step 4: Finalize setup
echo "Setup complete. You can now run the scripts locally."