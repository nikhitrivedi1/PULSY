# Create a chain for the RAG Pipeline 
from langchain.schema.runnable import RunnableLambda
from RAG.chain_llm import LLMChain
from RAG.chain_prompt import PromptChain
from DataSources.retriever_ops import PineconeClass
from DataSources.oura_data_aggregation import OuraData
from datetime import date, timedelta
import json
from DataSources.custom_api_key_error import APICallError


# RAGChain Class
# main LangChain pipeline for inference
class RAGChain:
    def __init__(self):
        self.llm = LLMChain()
    
    # Utilize user information to initialize device objects and chain element objects
    def init_personal(self, username, password):
        # Get relevant API Keys using username and password here
        oura_keys, pinecone_keys = self.retrieve_keys(username, password)
        try:
            #Pinecone API
            self.db = PineconeClass(pinecone_keys)
            # Oura API
            end_date = date.today()
            start_date = end_date - timedelta(days = 3)
            oura_data = OuraData(oura_keys, str(start_date), str(end_date))
            oura_data.sleep_data, oura_data.stress_data, oura_data.heart_rate_data = oura_data.pre_load_user_data()
            # Initialize the Prompt Chain
            self.prompt = PromptChain(oura_data)
        except APICallError as e:
            # return string as error
            return False, str(e)
        return True, "Success"

    # Get API Keys from user information
    # Current Implementation: DB is a file
    # Long Term Implementation: Store in web service
    def retrieve_keys(self, username, password):
        # PALCEHOLDER: come up with DB to retrieve relevant API Keys
        # For now - let's open up a db file with usernames and passwords encrypted
        with open('user_db.json', 'r') as f:
            user_dat = json.load(f)[username]
        
        oura_keys = user_dat['ouraKeys']


        # Get the PineconeDB Keys from the SystemDB
        with open('system_db.json', 'r') as s:
            sys_dat = json.load(s)["System"]
        
        pinecone_keys = sys_dat["Pinecone_API_KEY"]

        return oura_keys, pinecone_keys

    # Initialize LangChain chain with initialized components
    def create_chain(self):
        chain = (
            RunnableLambda(self.db.search) | # output: dict (documents, query)
            RunnableLambda(self.prompt.get_prompt) | # output: prompt
            RunnableLambda(self.llm.chat) | # output: response
            RunnableLambda(self.llm.format_response) # output: formatted response
        )
        return chain