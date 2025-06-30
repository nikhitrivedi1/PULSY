# Http GET Request Class for Wearable Devices

# Libraries
import requests
from DataSources.deviceENUM import Device
from requests.exceptions import RequestException, HTTPError, ConnectionError, TimeoutError

# HttpGETDevice Class
# Developed for all GET requests sent to API device endpoints
# Currently only considering the Oura Ring API
class HttpGETDevice():
    def __init__(self, deviceType: Device):
        self.deviceType = deviceType 

    # Executes GET Request given the input arguments
    # URL (str): url endpoint for the GET call
    # Params (dict): parameter component of the GET Request
    # Headers (dict): contains authentication information - {"Authorization": key}
    def sendRequest(self, URL: str, params: dict, header: dict):
        try:
            response = requests.request('GET', URL, headers = header, params = params)
            response.raise_for_status()
            return True, response.json()['data']
        except ConnectionError as e:
            # Couldn't connect with the server at all
            # Retry
            return False, str(e)
        except TimeoutError as t:
            # No response recieved within the timeout window
            # Retry
            return False, str(t)
        except HTTPError as http_error: 
            if response.status_code in {400, 401, 403, 422, 429}:
                # Client-Side Error Responses from Oura Ring API
                # Handle expected client-side errors
                resString = f"{self.deviceType.value} API Client Error {response.status_code}: {response.text}"
                return False, resString
            elif response.status_code >= 500 and response.status_code < 600: 
                resString = f"{self.deviceType.value} API Server Error {response.status_code}: Try again later."
                return False, resString
            else:
                resString = f"Unexpected Error: {http_error}"
                return False, resString
        except RequestException as r:
            return False, str(http_error)




