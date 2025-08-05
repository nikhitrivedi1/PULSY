# Pulsy - AI-Powered Wearable Insights 🧠⌚️

![Puley App Icon](src/assets/Pulsey_Icon.png)

**Understand your wearable data like never before with Puley. Get personalized, actionable insights inspired by experts like Andrew Huberman, powered by local AI.**

---

## How It Works ⚙️

1.  **Connect:** Link your compatible wearable device - currently supports the Oura RIng
2.  **Analyze:** Puley's local AI backend crunches your data with insights from Andrew Huberman
3.  **Learn:** Get easy-to-understand insights and recommendations.

## 🛠 Tech Stack
![Java_Swing](https://img.shields.io/badge/Java_Swing-Desktop_GUI-orange?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Python_API_Framework-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-RAG_Framework-005571?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-Local_Inference_Framework-8A2BE2?style=for-the-badge)
![Llama_3.2](https://img.shields.io/badge/Llama_3.2-Generator_Model-purple?style=for-the-badge)
![llama-text-embed-v2](https://img.shields.io/badge/llama_text_embed_v2-Retriever_Model-purple?style=for-the-badge)
![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-6A1B9A?style=for-the-badge)
![Oura_API](https://img.shields.io/badge/Oura_API-Wearable_Data-black?style=for-the-badge)

## Highlights ✨

* **Smart Analysis:** AI-driven insights from your HRV, sleep, activity, and more.
* **Huberman-Inspired:** Evidence-based tips for sleep, stress, and performance.
* **Local AI:** Powered by Ollama (Llama 3.1) for private and efficient analysis.
* **Desktop Native:** Built with Java Swing for a responsive experience.

## Download Instructions
The Java portion of this application can be run on an IDE and Java compiler of your choice. However, in order to utilize the LLM capabilities locally please follow the below instructions.
**Note this will download an LLM locally to your laptop so be aware of memory implications**

1. Clone the repository 
```
git clone [replace with link upon releasing to public]
```


2. Install pip dependencies for the RAG_API Package using the following command: 

```
cd backend/
```
```
pip install -r requirements.txt
```
2. Configure Ollama to pull and download a Llama 3.2 using (this download will take a while): 
```
ollama pull llama3.2
```

3. Next you will be able to set up the REST API to run locally on your laptop using the following cmd:
```
uvicorn main:app
```
4. From here - you can start the Java Application by going to frontend/Controller/AppController.java and running it

## TODO
- [ ] Add the average for the heart rate data (user_tools.py)
- [ ] Add the provisions for other devices (user_tools.py) 
- [ ] Narrow the scope only to the previous day (user_tools.py)
- [ ] Come up with DB to retrieve relevant API Keys - current implementation uses file, long term should store in web service (rag_chain.py)
---
