# Libraries
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Local Modules
from Agentic_RAG.agent import AgenticRAG
from user_tools import load_user_devices_service, load_user_goals_service

# QueryBody class - handles data validation for data passed in from frontend call
class QueryBody(BaseModel):
    query:str
    username:str
    user_history:list[str]
    ai_chat_history:list[str]

# LoadUserDevicesBody class - handles data validation for loading user metrics passed in from frontend call
class LoadUserDevicesBody(BaseModel):
    device_type: str
    device_name: str
    api_key: str

# Initialize Application Instance
app = FastAPI()

# Initialize AgenticRAG Instance
# One instance to rule them all
# User specific data is passed in as a query body
agent = AgenticRAG()

# Endpoint Agreement:
# device_type: str - the type of device to load [NEED TO SPECIFY SPECIFIC FORMAT]
# device_name: str - the name of the device to load
# api_key: str - api key for accessing current device data
# Returns: dict[str, str] - the result of the device loading
# Error Handling: HTTPException raised by load_user_devices_service
@app.post("/load_user_devices/")
async def load_user_devices(load_user_devices_body: LoadUserDevicesBody) -> dict[str, str|int|float]:
    result_data = await load_user_devices_service(load_user_devices_body.model_dump())
    return result_data

# Endpoint Agreement:
# user_id: str - the id of the user
# Returns: dict[str, str] - the result of the user goals loading
@app.get("/load_user_goals/{user_id}")
async def load_user_goals(user_id: str) -> dict[str, dict[str, str|list[dict]]]:
    result_data = await load_user_goals_service(user_id)
    return result_data

# Endpoint Agreement:
# query (QueryBody): user specific query body type checked by Pydantic class QueryBody
# returns res (str): LLM response to the invoked query
@app.post("/query/")
async def post_query(
    query: QueryBody
) -> str:
    # initialize the LLM upon running the instance
    # Pass in the query body to get a response
    res = agent.run(query.query, query.username, query.user_history, query.ai_chat_history)
    return res

# API ENDPOINT TEST ROUTE
@app.post("/queryTest/")
async def post_query_test(
    query: QueryBody
    )-> str:
    print(query.query, query.username, query.user_history, query.ai_chat_history)
    return "Test"

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

