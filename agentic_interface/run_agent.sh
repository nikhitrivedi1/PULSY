#!/bin/bash

# Function to handle cleanup on script exit
cleanup() {
    echo "Shutting down services..."
    kill $(jobs -p)
    exit
}

# Set up trap for cleanup
trap cleanup EXIT

# Start Agent Server in background
echo "Starting Agent Server..."
uvicorn main_agent:app &

# Wait for the Agent Server to finish
wait