# Create a chain for the RAG Pipeline 
from langchain.schema.runnable import RunnableLambda
from chainLLM import LLMChain
from chainPrompt import PromptChain
from DataSources.uploadToVectorStore import PineconeClass
from DataSources.ouraDataAggregation import OuraData
from datetime import date, timedelta


class RAGChain:
    def __init__(self):
        self.db = PineconeClass()
        # Initialize the Oura Data Aggregator
        endDate = date.today()
        startDate = endDate - timedelta(days = 3)
        self.ouraData = OuraData(str(startDate), str(endDate))
        # Initialize the Prompt Chain
        self.prompt = PromptChain(self.ouraData)
        # Initialize the LLM Chain
        self.llm = LLMChain()

    def createChain(self):
        chain = (
            RunnableLambda(self.db.search) | # output: dict (documents, query)
            RunnableLambda(self.prompt.getPrompt) | # output: prompt
            RunnableLambda(self.llm.chat) | # output: response
            RunnableLambda(self.llm.format) # output: formatted response
        )
        return chain