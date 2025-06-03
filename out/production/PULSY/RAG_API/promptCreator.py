# Libraires
from langchain.prompts import PromptTemplate
from DataSources.ouraDataAggregation import OuraData


class Prompt:
    def __init__(self, ouraData):
        # self.summary = "Your name is Pulsey and you are an AI that is meant to help users understand and extract value from their wearable device data." \
        #                 "Under weable data you will see the users data for sleep and stress from the Oura Ring along with contributing factors - use this data if a user asks for specific values" \
        #                 "Additionally you are equipped with a series of Documents that are transcripts directly from Andrew Huberman's youtube channel - use these insights to supplement your answer and always be sure to cite the information when used" \
        #                 " It is completely ok to not know the answer - if you don't have enough information let the user know. Provide a succinct and structured response - remember these users are coming to you because they do not understand their wearable data"\
        #                 " Given the wearable data information provided and the context documents provided - answer the question by presenting the numerical data first, and then walk the user through the answer"


        # TODO: Add instructions or definitions for each of the metric variables
        self.summary = ("Your name is Pulsey and you are a special AI advisor meant to help users understand and extract value from data derived from their wearable devices"
                        "Provided to you are several pieces of context that you should use when answering the users question - be clear, concise and keep your respones under 100 words"
                        "Under Wearable Data you will receive a summary of the users sleep data and stress data from the Oura Ring along with contributing factors - use the data directly to supplement your answer and always be sure to cite the information when responding"
                        "Additionally you are equipped with a series of documents that are transcripts from Andrew Huberman's podcasts - be sure to give Andrew credit for his insights and only provide succinct structures responses using this information if it correlates to insights you intend to provide based on sleep data"
                        "It is completely ok to not know the answer - if you don't have enough information let the user know "
                        "Your responses should be structures as follows: Present the numerical data from the device - explain what it means - use the Huberman podcast transcripts to provide insight")
        

        self.template = self.summary + "\n" + "Wearble Data: {userData}" + "\n" + "Documents:" + "\n"  "{documents}" + "\n\n" + "Question: {question}" + "\n"  
        self.prompt = PromptTemplate(template = self.template, input_variables = ["question", "documents", "userData"])
        self.ouraData = ouraData

    def getPrompt(self, question, documents):
        ouraDataForm = self.getOuraUserData(self.ouraData, question)
        return self.prompt.format(question  = question, documents = documents, userData = ouraDataForm)
    
    def getOuraUserData(self, ouraDat: OuraData, question):
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
            return "Sleep Scores: \n" + self.getSleepSummary(ouraDat) + "\n Stress Scores:" + self.getStressSummary(ouraDat)
        elif 'sleep' in question:
            return "Sleep Scores: \n" + self.getSleepSummary(ouraDat)
        elif 'stress' in question:
            return "Stress Scores:" + self.getStressSummary(ouraDat)
        else:
            return ""
    


    def getSleepSummary(self, ouraDat: OuraData):
        sleepSummary = []
        # Create arrays to store specifics of the sleep scores for formatting
        for data in ouraDat.sleepData:
            # format the information 
            sleepSummary.append(f"Date: {data['day']} | Sleep Score: {data['score']} | Contributors: Deep Sleep: {data['contributors']['deep_sleep']} Efficiency: {data['contributors']['efficiency']} Latency: {data['contributors']['latency']} REM:{data['contributors']['rem_sleep']} Restfulness: {data['contributors']['restfulness']} Timing: {data['contributors']['timing']} Total Sleep: {data['contributors']['total_sleep']}")

        # join the sleep summary chunks into a format
        sleepFormattedSummary = "\n".join(sleepSummary)
        return sleepFormattedSummary

    def getStressSummary(self, ouraDat: OuraData):
        stressSummary = []
        # Stress Scores
        for data in ouraDat.stressData:
            # format the information
            stressSummary.append(f"Date: {data['day']} | Max Stress Value: {data['stress_high']} | Recovery Max Value: {data['recovery_high']} | Day Summary: {data['day_summary']}")
        stressFormattedSummary = "\n".join(stressSummary)
        return stressFormattedSummary

