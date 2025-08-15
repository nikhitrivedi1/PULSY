# Data Aggregation Script - Oura Ring
# PROOF OF CONCEPT - FOCUS ON SLEEP, HEART RATE, STRESS

# Constants
BASEURL = "https://api.ouraring.com/v2/"
SLEEPURL = "usercollection/daily_sleep"
STRESSURL = "usercollection/daily_stress"
HRURL = "usercollection/heartrate"
MAXRETRY = 3

# Libraries
from datetime import datetime

from DataSources.get_request_devices import HttpGETDevice
from DataSources.device_enum import Device
from DataSources.custom_api_key_error import APICallError
from datetime import datetime, timedelta
from fastapi import HTTPException

# Class for the Oura Ring Device
# startDate: current Date - 3 days (to be modified to be more flexible)
# endDate: current Date
# Key: API Key from user
class OuraData:
    def __init__(self, key: str, start_date: str = str(datetime.now() - timedelta(days=3)), end_date: str = str(datetime.now())):
        # 3 Day Data Retrieval
        self.start_date = start_date
        self.end_date = end_date

        # Create Header
        self.header = {"Authorization": f"Bearer {key}"}

        # Data Attributes Initialized to None
        self.sleep_data = None
        self.stress_data = None
        self.heart_rate_data = None


    def pre_load_user_data(self) -> dict:
        # Initialize HTTP GET Request Object
        self.httpReq = HttpGETDevice(Device.OURA_RING)

        # get data response from the past 3 days
        result_data = self.query_execution()
        if "detail" not in result_data.keys():
            # Assign retrieved data to objects
            sleep_data = result_data["sleep_data"]
            stress_data = result_data["stress_data"]
            heart_rate_data = result_data["heart_rate_data"]
            return {"sleep_data": sleep_data, "stress_data": stress_data, "heart_rate_data": heart_rate_data}
        else:
            return result_data


    # Error Handling Update: 
    # 1. If the request fails, retry 3 times
    # 2. If the request fails after 3 retries, raise the error
    # 3. If the request returns a non-HTTPException, return the data

    # Execute Query to extract Sleep, Stress, and Heart Rate Data
    def query_execution(self) -> dict:
        execution_strings = [SLEEPURL, STRESSURL, HRURL]
        response_keys = ["sleep_data", "stress_data", "heart_rate_data"]
        result_data = {}

        for index, unique_url in enumerate(execution_strings):
            # Create url variations based on the data being loaded
            url = BASEURL + unique_url

            # unique format for HR Call
            if unique_url != HRURL: 
                params = {
                    'start_date': self.start_date,
                    'end_date': self.end_date
                }
            else:
                format = "%Y-%m-%d"
                params = {
                    'start_datetime': datetime.strptime(self.start_date, format),
                    'end_datetime': datetime.strptime(self.end_date, format)
            }

            # content (dict) -> indicator for whether request succeeded or failed
            content = self.httpReq.send_request(url, params, self.header)

            if isinstance(content, HTTPException):
                # retry call 3 times
                for _ in range(MAXRETRY):
                    content = self.httpReq.send_request(url, params, self.header)
                    if not isinstance(content, HTTPException):
                        break
                if isinstance(content, HTTPException):
                    raise content
            result_data[response_keys[index]] = content
        return result_data




        





