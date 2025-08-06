# Pulsy - Your AI Advisor for your Wearable Devices 🧠⌚️


**Transform your health data into actionable insights with Pulsy - an AI advisor that utilizes context from your Oura Ring data and documents from health experts (Andrew Huberman Labs) to provide you with ways to optimize your day**

---

## Overview 🌟
Pulsy combines a web interface with and Agentic RAG framework to help users gain insights from their health and wellness data. Key features include:
- **Pulsy - your Agent**: can retrieve relevant wearable data based on the question you ask it - this approach provides a generalizable process for your needs/questions

- **Goal-Based Workflow**: agentic capability to document, update and summarize your progress towards reaching your goals

- **Vector-Based Knowledge Retrieval**: RAG implementation using state-of-the-art embedding models to extract semantically relevant insights from documents

## System Architecture ⚙️

![System Architecture](readme_assets/Architecture_Diagram.png)



## Tech Stack 🛠

![Node.js](https://img.shields.io/badge/Node.js-Web_Framework-orange?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Python_API_Framework-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_RAG_Framework-005571?style=for-the-badge)
![GPT_4.1](https://img.shields.io/badge/GPT4.1-LLM-8A2BE2?style=for-the-badge)
![Llama_3.2](https://img.shields.io/badge/Llama_3.2-Generator_Model-purple?style=for-the-badge)
![llama-text-embed-v2](https://img.shields.io/badge/llama_text_embed_v2-Embedding_Model-purple?style=for-the-badge)
![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-6A1B9A?style=for-the-badge)
![Oura_API](https://img.shields.io/badge/Oura_API-Wearable_Data-black?style=for-the-badge)


## Demo Video 🎥
<video width="100%" controls>
  <source src="readme_assets/Pulsy_Demo.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>


---
## Getting Started 🚀


---
### ToDo's For The Repo
**AI Backend**

☐ Add proper 400 - 500 error code handling and raising for API interfaces

☐ Error handling - for FileNotFound type errors when accessing shared user_state.json and config.yaml

☐ Look into Pydantic methods to parse the response of the Oura Ring related tools - https://python.langchain.com/api_reference/core/output_parsers/langchain_core.output_parsers.openai_tools.PydanticToolsParser.html


**Web App**

☐ Refresh Chat page after Goal Creation to show the new goal element for user reference

**Overall**

☐ Host this application on the web
☐ Integrate GPT-OSS