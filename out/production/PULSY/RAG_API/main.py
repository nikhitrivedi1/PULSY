# Libraries
from fastapi import FastAPI 
import uvicorn
import numpy as np
from llmHandling import LLM
from ChainScripts.ragChain import RAGChain
import time

app = FastAPI()

startTime = time.time()
llm = LLM()
chain = RAGChain().createChain()
endTime = time.time()
# Time: 5.76187 s
print(f"LLM Initialization: {endTime - startTime}")

# @app.get("/items/{item_id}")
# def read_item(item_id: int):
#     return {"item_id": item_id}


# GET Methods
@app.get("/query/")
def getResponse(query: str, descriptions: str):
    # initialize the LLM upon running the instance
    # Pass in the query body to get a response
    startTime = time.time()
    # res = llm.chat(query, descriptions)
    res = chain.invoke(query)
    endTime = time.time()
    # Time: 34.1s 
    print(f"Response (llm.chat()): {endTime - startTime}")
    return res


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

