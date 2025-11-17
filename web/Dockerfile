# --- 1. Base Image ---
    FROM node:20-slim

    # --- 2. Working directory inside container ---
    WORKDIR /app
    
    # --- 3. Copy package files first (layer caching) ---
    COPY package*.json ./
    
    # --- 4. Install dependencies ---
    RUN npm install --production
    
    # --- 5. Copy the rest of the app ---
    COPY . .
    
    # --- 6. Expose port (Node frontend port) ---
    EXPOSE 3000
    
    # --- 7. Start the server ---
    CMD ["node", "server.js"]
    