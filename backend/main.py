# Libraries
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import numpy as np
from RAG.rag_chain import RAGChain
from user_tools import load_user_devices_service

# Error Messages 
INIT_ERROR_MESSAGE = "ERROR: Please ensure your device keys are properly documented"

# Query class - to handle baseline string - also to be used for any additional information that needs to be passed
class QueryBody(BaseModel):
    query:str
    username:str
    user_history:list[str]
    ai_chat_history:list[str]

# Initialize Globals
app = FastAPI()
chain_obj = RAGChain()
app.state.initializationComplete = False # Initialization Complete Flag

# GET METHODS

# Login - initialize RagChain objects per user information
# returns string of either success or error message
# Future Work: would like for this to provide information to the UI to indicate to the user what devices are available vs not
# username (str): 
# password (str)
@app.get("/login/")
async def login(username:str, password:str):
    success, message = chain_obj.init_personal(username, password)
    if success: 
        app.state.initializationComplete = True
        return "Success"
    return message


# POST Methods
# Query (str): user provided query for the LLM to answer
# Return (str):
# returns LLM response to the invoked query
# if initialization fails -> the initialization error message will be returned
@app.post("/query/")
async def post_query(
    query: QueryBody
):
    # Check Initialization
    if not app.state.initializationComplete:
        return INIT_ERROR_MESSAGE

    # initialize the LLM upon running the instance
    # Pass in the query body to get a response
    chain = chain_obj.create_chain()
    res = chain.invoke(query.query)
    return res

@app.post("/queryTest/")
async def post_query_test(
    query: QueryBody
    ):
    print(query.query, query.username, query.user_history, query.ai_chat_history)
    return "Test"

@app.get("/load_user_devices/")
async def load_user_devices(device_type: str, device_name: str, api_key: str):
    print(device_type, device_name, api_key)
    device_object = {
        "device_type": device_type,
        "device_name": device_name,
        "api_key": api_key
    }
    result_data = load_user_devices_service(device_object)
    return result_data

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

