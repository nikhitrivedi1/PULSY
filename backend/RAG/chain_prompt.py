# Libraires
from langchain.prompts import PromptTemplate
from DataSources.oura_data_aggregation import OuraData


class PromptChain:
    def __init__(self, oura_data):
        # TODO: Add instructions or definitions for each of the metric variables
        self.summary = ("Your name is Pulsey and you are a special AI advisor meant to help users understand and extract value from data derived from their wearable devices"
                        "Provided to you are several pieces of context that you should use when answering the users question - be clear, concise and keep your respones under 100 words"
                        "Under Wearable Data you will receive a summary of the users sleep data and stress data from the Oura Ring along with contributing factors - use the data directly to supplement your answer and always be sure to cite the information when responding"
                        "Additionally you are equipped with a series of documents that are transcripts from Andrew Huberman's podcasts - be sure to give Andrew credit for his insights and only provide succinct structures responses using this information if it correlates to insights you intend to provide based on sleep data"
                        "It is completely ok to not know the answer - if you don't have enough information let the user know "
                        "Your responses should be structures as follows: Present the numerical data from the device - explain what it means - use the Huberman podcast transcripts to provide insight")
        
        self.template = self.summary + "\n" + "Wearble Data: {user_data}" + "\n" + "Documents:" + "\n"  "{documents}" + "\n\n" + "Question: {question}" + "\n"  
        self.prompt = PromptTemplate(template = self.template, input_variables = ["question", "documents", "user_data"])
        self.oura_data = oura_data

    def get_prompt(self, db_response: dict):
        question = db_response["query"]
        documents = db_response["documents"]
        oura_data_form = self.get_oura_user_data(self.oura_data, question)
        return self.prompt.format(question  = question, documents = documents, user_data = oura_data_form)
    
    def get_oura_user_data(self, oura_data: OuraData, question):
        # Sleep Scores
            #         {
            #   "data": [
            #     {
            #       "id": "string",
            #       "contributors": {
            #         "deep_sleep": 0,
            #         "efficiency": 0,
            #         "latency": 0,
            #         "rem_sleep": 0,
            #         "restfulness": 0,
            #         "timing": 0,
            #         "total_sleep": 0
            #       },
            #       "day": "2019-08-24",
            #       "score": 0,
            #       "timestamp": "string"
            #     }
            #   ],
            #   "next_token": "string"
            # }

        # Based on the Question - check for inclusion of stress - sleep as well as stress and sleep

        if 'sleep' in question and 'stress' in question:
            return "Sleep Scores: \n" + self.get_sleep_summary(oura_data) + "\n Stress Scores:" + self.get_stress_summary(oura_data)
        elif 'sleep' in question:
            return "Sleep Scores: \n" + self.get_sleep_summary(oura_data)
        elif 'stress' in question:
            return "Stress Scores:" + self.get_stress_summary(oura_data)
        else:
            return ""
    
    def get_sleep_summary(self, oura_data: OuraData):
        sleep_summary = []
        # Create arrays to store specifics of the sleep scores for formatting
        for data in oura_data.sleep_data:
            # format the information 
            sleep_summary.append(f"Date: {data['day']} | Sleep Score: {data['score']} | Contributors: Deep Sleep: {data['contributors']['deep_sleep']} Efficiency: {data['contributors']['efficiency']} Latency: {data['contributors']['latency']} REM:{data['contributors']['rem_sleep']} Restfulness: {data['contributors']['restfulness']} Timing: {data['contributors']['timing']} Total Sleep: {data['contributors']['total_sleep']}")

        # join the sleep summary chunks into a format
        sleep_formatted_summary = "\n".join(sleep_summary)
        return sleep_formatted_summary

    def get_stress_summary(self, oura_data: OuraData):
        stress_summary = []
        # Stress Scores
        for data in oura_data.stress_data:
            # format the information
            stress_summary.append(f"Date: {data['day']} | Max Stress Value: {data['stress_high']} | Recovery Max Value: {data['recovery_high']} | Day Summary: {data['day_summary']}")
        stress_formatted_summary = "\n".join(stress_summary)
        return stress_formatted_summary

