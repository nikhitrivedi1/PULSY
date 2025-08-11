# Pulsy - Your AI Advisor for your Wearable Devices 🧠⌚️

![Version](https://img.shields.io/badge/version-0.1.0-blue)

Pulsy turns your wearable data into **personalized, expert-backed insights** — powered by agentic AI workflows and curated health knowledge from voices like *Andrew Huberman*.
---

### 🚀 What Pulsy Does

- 📊 **Wearable Integration**  
  Pulls sleep, stress, and heart rate data from your **Oura Ring**.

- 🔍 **Smart Retrieval**  
  Uses **RAG (Retrieval-Augmented Generation)** to surface semantically relevant insights from a vector database.


- 🎯 **Goal Tracking**  
  Creates, manages, and documents progress toward your personal health goals.

---

> 💡 *Pulsy bridges the gap between raw health metrics and actionable, science-driven insights.*


## Demo 🎥 🎬
▶️ [Watch the Pulsy Demo Video](readme_assets/Pulsy_Demo.mp4)


## Tech Stack 🛠

![Node.js](https://img.shields.io/badge/Node.js-Web_Framework-orange?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Python_API_Framework-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_RAG_Framework-005571?style=for-the-badge)
![GPT_4.1](https://img.shields.io/badge/GPT4.1-LLM-8A2BE2?style=for-the-badge)
![bert-large-nli-stsb-mean-tokens](https://img.shields.io/badge/bert_large_nli_stsb-Embedding_Model-purple?style=for-the-badge)
![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-6A1B9A?style=for-the-badge)
![Oura_API](https://img.shields.io/badge/Oura_API-Wearable_Data-black?style=for-the-badge)
## System Architecture ⚙️
*Local JSON DB subject to change in next hosted version*
<p align="center">
  <img src="readme_assets/Architecture_Diagram.png" alt="System Architecture">
</p>

---
## Getting Started 🚀
### Prerequisites
- Python 3.9+
- Node.js
- npm
- API Keys for: Oura Ring, Pinecone, OpenAI

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/nikhitrivedi1/PULSY.git
   cd Pulsy
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Node.js dependencies:
   ```bash
   npm install
   ```

4. Configure API Keys:
   - Copy `config/config.example.yaml` to `config.yaml`
   - Update the following values in `config.yaml` 
     ```yaml
     OPENAI_API_KEY: "YOUR_OPENAI_API_KEY"  # OpenAI API key for LLM functionality
     PINECONE_API_KEY: "YOUR_PINECONE_API_KEY"  # Pinecone API key for vector storage
     PINECONE_HOST: "YOUR_PINECONE_HOST"  # Your Pinecone host URL
     PINECONE_INDEX: "YOUR_PINECONE_INDEX"  # Name of your Pinecone index
     PINECONE_EMBEDDING_MODEL: "YOUR_PINECONE_EMBEDDING_MODEL"  # Embedding model name
     ```
     *Note that you will need to provide your own documents via Pinecone for this version (upgrade will come in the next version)*

5. Navigate to the web directory:
   ```bash
   cd web
   ```

6. Start the web server:
   ```bash
   ./run.sh
   ```

7. In a new terminal, navigate to the agent interface:
   ```bash
   cd agentic_interface
   ```

8. Start the agent server:
   ```bash
   ./run_agent.sh
   ```

9. Access the application:
   - Open your browser and navigate to `http://localhost:3000/`
   - Click the "Create Profile" button to set up your account
   - Start exploring your health insights!

### *Note: Make sure both terminal windows remain open while using the application. The web server and agent server need to run simultaneously for full functionality*

---
## Coming Soon! 🚀
✨ Hosted Agentic RAG service - Stay tuned 🌟
