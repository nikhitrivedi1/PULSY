# Data Aggregation Script - Oura Ring
# PROOF OF CONCEPT - FOCUS ON SLEEP, HEART RATE, STRESS

# Constants
BASEURL = "https://api.ouraring.com/v2/"
SLEEPURL = "usercollection/daily_sleep"
STRESSURL = "usercollection/daily_stress"
HRURL = "usercollection/heartrate"
MAXRETRY = 3

# Libraries
import requests
from datetime import datetime
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout

from DataSources.httpGETClass import HttpGETDevice
from DataSources.deviceENUM import Device

# Class for the Oura Ring Device
# startDate: current Date - 3 days (to be modified to be more flexible)
# endDate: current Date
# Key: API Key from user
class OuraData:
    def __init__(self, startDate, endDate, key):
        # 3 Day Data Retrieval
        self.startDate = startDate
        self.endDate = endDate

        # Initialize HTTP GET Request Object
        self.httpReq = HttpGETDevice(Device.OURA_RING)

        # Create Header
        self.header = {'Authorization': f'Bearer {key}'}

        # get data response from the past 3 days
        resultData = self.queryExecution()

        # Assign retrieved data to objects
        self.sleepData = resultData[0]
        self.stressData = resultData[1]
        self.hearRateData = resultData[2]

    # Execute Query to extract Sleep, Stress, and Heart Rate Data
    def queryExecution(self):
        executionStrings = [SLEEPURL, STRESSURL, HRURL]
        resultData = []

        for uniqueURL in executionStrings:
            # Create url variations based on the data being loaded
            url = BASEURL + uniqueURL

            # unique format for HR Call
            if(uniqueURL != HRURL): 
                params = {
                    'start_date': self.startDate,
                    'end_date': self.endDate
                }
            else:
                format = "%Y-%m-%d"
                params = {
                    'start_datetime': datetime.strptime(self.startDate, format),
                    'end_datetime': datetime.strptime(self.endDate, format)
            }

            # success (bool) -> indicator for whether request succeeded or failed
            success, content = self.httpReq.sendRequest(url, params, self.header)

            if not success: 
                # retry call 3 times
                attempt = 1
                while(attempt < MAXRETRY and not success):
                    success, content = self.httpReq.sendRequest(url, params, self.header)
                    if(success): break
                    attempt+=1
                
                if(not success):
                    raise RuntimeError(content)
            
            resultData.append(content)
        return resultData




        





