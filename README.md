# Pulsy — Your AI Advisor for Wearable Device Data 🧠⌚️

Pulsy transforms your wearable data into **personalized, expert-grounded health insights**, powered by **agentic AI**, **RAG**, and curated scientific knowledge (inspired by voices like *Andrew Huberman*).

👉 **Try it live:** https://pulsy-768224718837.us-west1.run.app/

---

## ✨ What Pulsy Does

- **📊 Meaningful Wearable Integration**  
  Pulls your **Oura Ring** sleep, stress, Heart Rate.

- **🔍 Smart Retrieval (RAG)**  
  Uses embeddings + vector search to surface the most relevant scientific insights to your physiology.

- **🧠 Agentic Reasoning Loops**  
  LangGraph powers multi-step reasoning over:  
  – your biometric trends  
  – retrieved micro-insights  
  – domain guidance (sleep, stress, heart rate)
  - your response preferences

- **📚 Expert-Backed Health Knowledge**  
  Curated guidance sourced from:  
  • Huberman Lab
---

## 🛠 Tech Stack

![Node.js](https://img.shields.io/badge/Node.js-Web_Framework-orange?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Python_API_Framework-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_RAG_Framework-005571?style=for-the-badge)
![OpenAI GPT-4.1](https://img.shields.io/badge/GPT4.1-LLM-8A2BE2?style=for-the-badge)
![BERT](https://img.shields.io/badge/bert_large_nli_stsb-Embedding_Model-purple?style=for-the-badge)
![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-6A1B9A?style=for-the-badge)
![Oura API](https://img.shields.io/badge/Oura_API-Wearable_Data-black?style=for-the-badge)
![GCP](https://img.shields.io/badge/GCP-Cloud_Run_Deployment-orange?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-User_%26_Logging_DB-purple?style=for-the-badge)

---

## 🧩 System Architecture (High-Level)

**Pulsy** is built as a modular AI pipeline composed of:

1. **Frontend (Node.js/EJS)** – session management, UI, routing  
2. **Backend API (FastAPI)** – wearable ingestion, RAG retrieval, model execution  
3. **Agent Layer (LangGraph)** – orchestrates tool calls, retrieval, and reasoning  
4. **Vector Store (Pinecone)** – semantic search over curated health corpus  
5. **PostgreSQL** – users, device bindings, logs, and session insights  

---

## 🗺 Roadmap / TODO

### 🟩 Core Improvements
- [ ] Optimize Retrieval via evaluating different Chunking/Overlap   
- [ ] Expand health corpus to training load, circadian, recovery, metabolic health
- [ ] Create comprehensive Evaluation Framework to quantify performance of Agent


### 🧪 AI / Modeling
- [ ] Transition from OpenAI API to local LLM via Ollama
- [ ] SFT on application specific dataset 

### 📱 Future Integrations
- [ ] Apple HealthKit  
- [ ] WHOOP

---

## 🤝 Contributing

If you have ideas, suggestions, or improvements, **I would love to learn from you**.  
Feel free to open an issue or **submit a PR** — especially if you’d like to collaborate on:

- agentic workflows  
- health-focused RAG systems  
- app design and usability  
