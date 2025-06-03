# LLM Query and Response Handling

# Libraries
# Ollama Libraries - for chat
from ollama import chat
from ollama import ChatResponse

#Pinecone and LangChain Libraries
from ChainScripts.chainPrompt import PromptChain
# from .llmHandling import LLM

# MISC
import markdown


class LLMChain():
    def __init__(self):
         # Model name
        # 3.2b params
        self.modelName = 'llama3.2'


    def chat(self, prompt):
        response: ChatResponse = chat(
            model = self.modelName,
            messages = [
                {
                    'role': 'user',
                    'content': prompt
                },
            ]
        )
        return response

    def format(self, response):
        # TODO: NEED GENERIC WAY TO FORMAT - this is ANNOYING
        unformattedRespose = response['message']['content']
        unformattedRespose = unformattedRespose.replace("\n", "<br>")
        print(unformattedRespose)

        # Format to remove the \n
        htmlResponse = markdown.markdown(unformattedRespose)
        return htmlResponse






        
