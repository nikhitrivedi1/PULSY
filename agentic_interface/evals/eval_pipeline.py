# Eval Pipeline for the Agentic RAG System
from Agentic_RAG.agent import AgenticRAG
import json
from collections import defaultdict
from openai import OpenAI
from config.settings import settings
import os
import asyncio
class EvalPipeline: 
    def __init__(self):
        self.agent = AgenticRAG()
        self.input_arr = self._load_evals_data("evals/pulsy_evals_v1.jsonl")
        self.user_id = "trivedi.nik"
        self.system_instructions = self._load_system_instructions("Agentic_RAG/system_instructions_Ollama.md")
        self.client = OpenAI(
            api_key = os.getenv("OPENAI_API_KEY")
        )

        with open("evals/eval_prompt.md", "r") as file:
            self.grade_prompt = file.read()

        self.passing = 0 
        self.fail = 0


        self.response_schema =  {
            "type": "object",
            "properties": {
                "STATUS": {
                    "type": "string",
                    "enum": ["PASS", "FAIL"]
                },
                "COMMENTS": {
                    "type": "string"
                },
                "ERROR_CATEGORY": {
                    "type": "string",
                    "enum": ["incorrect tool calling", "answer generation", "non-compliant workflow", "inventing information", "improper formatting", "other"]
                }
            },
            "required": ["STATUS", "COMMENTS", "ERROR_CATEGORY"],
            "additionalProperties": False
        }

    async def evals_run(self):
        results = []
        for input in self.input_arr:
            print(f"Evaluating: {input['id']}")
            try:
                latest_query = input['messages'][-1]['content']
                user_history = []
                ai_history = []

                for message in input['messages'][:-1]:
                    if message['role'] == 'user':
                        user_history.append(message['content'])
                    else:
                        ai_history.append(message['content'])

                config = {
                    "configurable": {
                        "thread_id": f"eval_{input['id']}",
                        "model": "smolLM2_1.7B"
                    },
                    "recursion_limit": 10
                }
                # Make Call to the Backend Agent
                response = await self.agent.run(latest_query, self.user_id, user_history, ai_history, eval_mode=True, config=config)

                

                # Create Input Prompt for Grading
                input_example= (
                    f"Query: {latest_query}\n"
                    f"Tool Calls: {response['tool_calls']}\n"
                    f"Response: {response['response']}"
                )

            except Exception as e:
                results.append({"STATUS": "FAIL", "CATEGORY": input['category'], "COMMENT": str(e), "ERROR_CATEGORY": "unknown"})
                print(f"Graded: {input['id']} w/ error: {e}")
                self.fail += 1
                print(f"Passing: {self.passing} | Failing: {self.fail}")
                continue
            
            graded_response = self._grade_evals(input_example)
            graded_response['CATEGORY'] = input['category']
            graded_response['ERROR_CATEGORY'] = graded_response['ERROR_CATEGORY']

            results.append(graded_response)
            if graded_response['STATUS'] == "PASS":
                self.passing += 1
            else:
                self.fail += 1
            print(f"Passing: {self.passing} | Failing: {self.fail}")
        return results
    

    def _grade_evals(self, input_example:str):
        response = self.client.responses.create(
            model="gpt-4o-mini",
            instructions = self.grade_prompt,
            input=f"System Instructions: {self.system_instructions}\n{input_example}",
            text={
                "format": {
                    "type": "json_schema",
                    "schema": self.response_schema,
                    "name": "eval_response",
                    "strict": True,
                }
            },
        )
        try:
            results = json.loads(response.output[0].content[0].text)
        except Exception as e:
            print(f"Clean Text: {response}")
            print(f"Error: {e}")
            return {"STATUS": "UNKNOWN", "COMMENT": response, "ERROR_CATEGORY": "unknown"}
            
        return {"STATUS": results["STATUS"], "COMMENT": results["COMMENTS"], "ERROR_CATEGORY": results["ERROR_CATEGORY"]}


    def _load_evals_data(self, file_path: str) -> list[dict]:
        rows = []
        with open(file_path, "r") as file:
            for enum, line in enumerate(file):
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def _load_system_instructions(self, file_path: str) -> str:
        with open(file_path, "r") as file:
            return file.read()

if __name__ == "__main__":
    eval_pipeline = EvalPipeline()
    graded = asyncio.run(eval_pipeline.evals_run())
    # write to a json file
    with open("evals/pulsy20b_evals_v1.json", "w") as file:
        json.dump(graded, file, indent=4)