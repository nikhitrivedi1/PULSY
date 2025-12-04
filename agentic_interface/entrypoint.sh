#!/bin/bash


# Serve Ollama Server
echo 'Starting Ollama Server'
ollama serve &

# Ensure Model is Downloaded
echo 'Pulling Smollm2:1.7B Model'
sleep 5
ollama pull smollm2:1.7b


# Start FastAPI Server
echo 'Starting FastAPI Server'
uvicorn main_agent:app --host 0.0.0.0 --port 8080
