# Data Aggregation Script - Oura Ring
# PROOF OF CONCEPT - FOCUS ON SLEEP, HEART RATE, STRESS


# Constants
APIKEY = "UNEWV6S7AQ4F3FHYKJZW2SBXN5N2YRDJ"
BASEURL = "https://api.ouraring.com/v2/"
SLEEPURL = "usercollection/daily_sleep"
STRESSURL = "usercollection/daily_stress"
HRURL = "usercollection/heartrate"

# Libraries
import requests
from datetime import datetime
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout


class OuraData:
    def __init__(self, startDate, endDate):
        self.startDate = startDate
        self.endDate = endDate
        self.params = {
            'start_date': startDate,
            'end_date': endDate
        }
        # Create Header
        self.header = {'Authorization': f'Bearer {APIKEY}'}
        self.sleepData = self.queryExecution(SLEEPURL)
        self.stressData = self.queryExecution(STRESSURL)
        self.hearRateData = self.queryExecution(HRURL)


    def queryExecution(self, uniqueURL):
        # Create Query details
        url = BASEURL + uniqueURL

        try:
            if(uniqueURL != HRURL):
                response = requests.request('GET', url, headers=self.header, params = self.params)
            else:
                # Need to update dtype params for the heart rate query
                # format YYYY-MM-DD
                format = "%Y-%m-%d"
                params = {
                    'start_datetime': datetime.strptime(self.startDate, format),
                    'end_datetime': datetime.strptime(self.endDate, format)
                }
                response = requests.request('GET', url, headers=self.header, params = self.params)

        except ConnectionError as e:
            print(e)
        except TimeoutError as t:
            # handle
            print(t)
        except HTTPError as h:
            print(h)
        except RequestException as r:
            print(r)
        finally:
            print("Request Successfully Excecuted")

        return response.json()['data']




        





