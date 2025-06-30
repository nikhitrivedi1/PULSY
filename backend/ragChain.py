# Create a chain for the RAG Pipeline 
from langchain.schema.runnable import RunnableLambda
from chainLLM import LLMChain
from chainPrompt import PromptChain
from DataSources.uploadToVectorStore import PineconeClass
from DataSources.ouraDataAggregation import OuraData
from datetime import date, timedelta
import json

# RAGChain Class
# main LangChain pipeline for inference
class RAGChain:
    def __init__(self):
        self.llm = LLMChain()
    
    # Utilize user information to initialize device objects and chain element objects
    def initPersonal(self, username, password):
        # Get relevant API Keys using username and password here
        ouraKeys, pineconeKeys = self.retrieveKeys(username, password)
        try:
            #Pinecone API
            self.db = PineconeClass(pineconeKeys)
            # Oura API
            endDate = date.today()
            startDate = endDate - timedelta(days = 3)
            self.ouraData = OuraData(str(startDate), str(endDate), ouraKeys)
            # Initialize the Prompt Chain
            self.prompt = PromptChain(self.ouraData)
        except RuntimeError as e:
            # return string as error
            return False, str(e)
        return True, "Success"

    # Get API Keys from user information
    # Current Implementation: DB is a file
    # Long Term Implementation: Store in web service
    def retrieveKeys(self, username, password):
        # PALCEHOLDER: come up with DB to retrieve relevant API Keys
        # For now - let's open up a db file with usernames and passwords encrypted
        with open('userDB.json', 'r') as f:
            userDat = json.load(f)[username]
        
        ouraKeys = userDat['ouraKeys']


        # Get the PineconeDB Keys from the SystemDB
        with open('systemDB.json', 'r') as s:
            sysDat = json.load(s)["System"]
        
        pineconeKeys = sysDat["Pinecone_API_KEY"]

        return ouraKeys, pineconeKeys

    # Initialize LangChain chain with initialized components
    def createChain(self):
        chain = (
            RunnableLambda(self.db.search) | # output: dict (documents, query)
            RunnableLambda(self.prompt.getPrompt) | # output: prompt
            RunnableLambda(self.llm.chat) | # output: response
            RunnableLambda(self.llm.format) # output: formatted response
        )
        return chain