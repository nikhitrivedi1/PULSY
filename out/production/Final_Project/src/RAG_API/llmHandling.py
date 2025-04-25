# LLM Query and Response Handling

# Libraries
# Ollama Libraries - for chat
from ollama import chat
from ollama import ChatResponse

#Pinecone and LangChain Libraries
from DataSources.uploadToVectorStore import PineconeClass
from langchain_huggingface import HuggingFaceEmbeddings
from promptCreator import Prompt

# Data Aggregators
from DataSources.ouraDataAggregation import OuraData

# MISC
from datetime import date, timedelta
import markdown
import time


class LLM:
    def __init__(self):
        # Initialize DB
        self.db = PineconeClass()

        # Model name
        # 3.2b params
        self.modelName = 'llama3.2'

        # Aggregate the Latest Oura Data (from the past 3 days)
        endDate = date.today()
        startDate = endDate - timedelta(days = 3)

        start = time.time()
        # time: Oura Data API Call 1.5327s 
        self.ouraData = OuraData(str(startDate), str(endDate))
        end = time.time()
        print(f"Oura Data API Call {end - start}")


    def chat(self, query, descriptions):
        # get necessary documents
        start = time.time()
        _ = self.db.search(query, "podcastTranscripts")
        textDocs = self.db.extractText()
        end = time.time()
        print(f"Pinecone Search and Document Extraction: {end-start}")
        
        # Create a Prompt using the prompt template
        prompt = Prompt().getPrompt(query,"\n".join(textDocs),self.ouraData, descriptions)

        start = time.time()
        response: ChatResponse = chat(
            model = self.modelName,
            messages = [
                {
                    'role': 'user',
                    'content': prompt
                },
            ]
        )
        print(response)
        end = time.time()
        print(f"LLM Response (ChatResponse): {end - start}")



        # TODO: NEED GENERIC WAY TO FORMAT - this is ANNOYING
        unformattedRespose = response['message']['content']
        unformattedRespose = unformattedRespose.replace("\n", "<br>")
        print(unformattedRespose)

        # Format to remove the \n


        htmlResponse = markdown.markdown(unformattedRespose)
        return htmlResponse






        
