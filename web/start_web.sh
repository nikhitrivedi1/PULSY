#!/bin/bash

# Check and copy config files if they don't exist
if [ ! -f "config/config.yaml" ]; then
    cp config/config.example.yaml config/config.yaml
fi

if [ ! -f "shared/user_state.json" ]; then
    cp shared/user_state.example.json shared/user_state.json
fi

# Function to handle cleanup on script exit
cleanup() {
    echo "Shutting down services..."
    kill $(jobs -p)
    exit
}

# Set up trap for cleanup
trap cleanup EXIT

# Start web server in background
echo "Starting web server..."
node server.js &

# Wait for both processes
wait
