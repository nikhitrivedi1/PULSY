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


    def pre_load_user_data(self):
        # Initialize HTTP GET Request Object
        self.httpReq = HttpGETDevice(Device.OURA_RING)

        # get data response from the past 3 days
        try:
            result_data = self.query_execution()
        except APICallError as e:
            raise APICallError(str(e))

        # Assign retrieved data to objects
        sleep_data = result_data[0]
        stress_data = result_data[1]
        heart_rate_data = result_data[2]
        return sleep_data, stress_data, heart_rate_data


    # Execute Query to extract Sleep, Stress, and Heart Rate Data
    def query_execution(self):
        execution_strings = [SLEEPURL, STRESSURL, HRURL]
        result_data = []

        for unique_url in execution_strings:
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

            # success (bool) -> indicator for whether request succeeded or failed
            success, content = self.httpReq.send_request(url, params, self.header)

            if not success: 
                # retry call 3 times
                for _ in range(MAXRETRY):
                    success, content = self.httpReq.send_request(url, params, self.header)
                    if success: break

                if not success:
                    raise APICallError(content)
            
            result_data.append(content)
        return result_data




        





