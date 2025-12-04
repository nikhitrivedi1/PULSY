###############################################
# Cloud Run GPU + CUDA + Ollama + FastAPI
###############################################

# 1. Base image with NVIDIA CUDA runtime
FROM ollama/ollama

# 2. Install basic dependencies
RUN apt-get update && apt-get install -y python3 python3-pip vim 

# 4. Working directory
WORKDIR /app

# 5. Install Python requirements
COPY requirements.txt .
RUN pip install --break-system-packages pip && pip install --break-system-packages -r requirements.txt

# 6. Copy FastAPI code
COPY . .

# # 7. Preload a model
# RUN ollama pull llama3

# Make sure the script is executable
RUN chmod +x entrypoint.sh

# Cloud Run listens on port 8080
EXPOSE 8080
# Ollama internal port
EXPOSE 11434

ENTRYPOINT ["./entrypoint.sh"]