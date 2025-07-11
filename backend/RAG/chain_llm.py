# LLM Query and Response Handling

# Libraries
# Ollama Libraries - for chat
from ollama import chat
from ollama import ChatResponse

# MISC
import markdown


class LLMChain():
    def __init__(self):
         # Model name
        # 3.2b params
        self.model_name = 'llama3.2'


    def chat(self, prompt):
        response: ChatResponse = chat(
            model = self.model_name,
            messages = [
                {
                    'role': 'user',
                    'content': prompt
                },
            ]
        )
        return response

    def format_response(self, response):
        # TODO: NEED GENERIC WAY TO FORMAT - this is ANNOYING
        unformatted_response = response['message']['content']
        unformatted_response = unformatted_response.replace("\n", "<br>")
        print(unformatted_response)

        # Format to remove the \n
        html_response = markdown.markdown(unformatted_response)
        return html_response






        
