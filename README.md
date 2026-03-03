# Pulsy — Agentic RAG for Wearable Health Intelligence

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Pulsy-111827?style=for-the-badge&logo=googlechrome&logoColor=white)](https://pulsy-768224718837.us-west1.run.app/)
[![URL](https://img.shields.io/badge/URL-pulsy--768224718837.us--west1.run.app-334155?style=for-the-badge)](https://pulsy-768224718837.us-west1.run.app/)


Pulsy is an agentic retrieval-augmented generation (RAG) system that transforms Oura Ring data into personalized, evidence-grounded health guidance.


## What Problem Does Pulsy Solve?

Raw wearable metrics (sleep score, HRV, stress) lack context.
Pulsy bridges biometric trends with curated scientific micro-insights through structured retrieval and agentic reasoning loops.


## 📊 System Performance Overview

> Metrics evaluated on the same benchmark dataset.


<table align="center" style="width:100%;">
  <tr>
    <th><div align="center">Metric</div></th>
    <th><div align="center">Baseline (v0)</div></th>
    <th><div align="center">Optimized (v1)</div></th>
    <th><div align="center">Δ Improvement</div></th>
    <th width="45%"><div align="center">Notes</div></th>
  </tr>

  <tr>
    <td align="center">Tool Call Accuracy</td>
    <td align="center"><span style="color:#2da44e"><b>0.90</b></span></td>
    <td align="center"><span style="color:#2da44e"><b>0.90</b></span></td>
    <td align="center">—</td>
    <td align="center"><sub>No change</sub></td>
  </tr>

  <tr>
    <td align="center">Precision@3</td>
    <td align="center"><span style="color:#d73a49"><b>0.36</b></span></td>
    <td align="center"><span style="color:#2da44e"><b>0.68</b></span></td>
    <td align="center"><span style="color:#2da44e"><b>+90%</b></span></td>
    <td align="center"><sub>Embedding → <code>llama-text-embed-v2</code> · Chunking → <code>cs500/co100</code></sub></td>
  </tr>

  <tr>
    <td align="center">Hits@3</td>
    <td align="center"><span style="color:#d73a49"><b>0.60</b></span></td>
    <td align="center"><span style="color:#2da44e"><b>0.91</b></span></td>
    <td align="center"><span style="color:#2da44e"><b>+51%</b></span></td>
    <td align="center"><sub>Embedding → <code>llama-text-embed-v2</code> · Chunking → <code>cs500/co100</code></sub></td>
  </tr>

  <tr>
    <td align="center">MRR@3</td>
    <td align="center"><span style="color:#d73a49"><b>0.48</b></span></td>
    <td align="center"><span style="color:#2da44e"><b>0.76</b></span></td>
    <td align="center"><span style="color:#2da44e"><b>+61%</b></span></td>
    <td align="center"><sub>Embedding → <code>llama-text-embed-v2</code> · Chunking → <code>cs500/co100</code></sub></td>
  </tr>

  <tr>
    <td align="center">p50 Latency (E2E)</td>
    <td align="center"><span style="color:#2da44e"><b>6.26s</b></span></td>
    <td align="center"><span style="color:#2da44e"><b>6.26s</b></span></td>
    <td align="center">—</td>
    <td align="center"><sub>No change</sub></td>
  </tr>

  <tr>
    <td align="center">p95 Latency (E2E)</td>
    <td align="center"><span style="color:#e3b341"><b>27.05s</b></span></td>
    <td align="center"><span style="color:#e3b341"><b>27.05s</b></span></td>
    <td align="center">—</td>
    <td align="center"><sub>Tail latency debugging in progress</sub></td>
  </tr>
</table>





## 🛠 Tech Stack

<p align="center">
  <img alt="Node.js" src="https://img.shields.io/badge/Node.js-Web_Framework-orange?style=for-the-badge" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-Python_API_Framework-005571?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img alt="LangGraph" src="https://img.shields.io/badge/LangGraph-Agentic_RAG_Framework-005571?style=for-the-badge" />
  <img alt="OpenAI GPT-4.1" src="https://img.shields.io/badge/GPT4.1-LLM-8A2BE2?style=for-the-badge" />
  <img alt="Embeddings" src="https://img.shields.io/badge/Embedding_Model-llama_text_embed_v2-purple?style=for-the-badge" />
  <img alt="Pinecone" src="https://img.shields.io/badge/Pinecone-Vector_DB-6A1B9A?style=for-the-badge" />
  <img alt="Oura API" src="https://img.shields.io/badge/Oura_API-Wearable_Data-black?style=for-the-badge" />
  <img alt="GCP" src="https://img.shields.io/badge/GCP-Cloud_Run_Deployment-orange?style=for-the-badge" />
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-User_%26_Logging_DB-purple?style=for-the-badge" />
</p>

---

## 🧩 System Architecture (High-Level)

**Pulsy** is built as a modular AI pipeline composed of:

1. **Frontend (Node.js/EJS)** – session management, UI, routing  
2. **Backend API (FastAPI)** – wearable ingestion, RAG retrieval, stateless inference 
3. **Agent Layer (LangGraph)** – orchestrates tool calls, retrieval, and reasoning  
4. **Vector Store (Pinecone)** – semantic search over curated health corpus  
5. **PostgreSQL** – users, device bindings, logs, and session insights  

### Agentic Architecture Diagram
![Pulsy Architecture](readme_assets/Pulsy_Architecture_Diagram.png)

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
