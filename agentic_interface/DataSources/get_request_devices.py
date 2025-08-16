# Http GET Request Class for Wearable Devices

# Libraries
import requests
from requests.exceptions import HTTPError
from DataSources.device_enum import Device
from fastapi import HTTPException


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
    def send_request(self, URL: str, params: dict, header: dict) -> dict:
        try:
            response = requests.get(
                URL, 
                headers = header, 
                params = params
            )
            response.raise_for_status()
            return response.json()['data']
        except HTTPError as http_error: 
            if response.status_code in {400, 401, 403, 422, 429}:
                # Client-Side Error Responses from Oura Ring API
                # Handle expected client-side errors
                resString = f"{self.deviceType.value} API Client Error {response.status_code}: {response.json()['message']}"
                raise HTTPException(status_code=response.status_code, detail=resString)
            elif response.status_code >= 500 and response.status_code < 600:
                # For internal server errors - don't send back details of the error message as this is internal 
                resString = f"{self.deviceType.value} API Server Error {response.status_code}: Try again later."
                raise HTTPException(status_code=response.status_code, detail=resString)
            else:
                # General Error Code
                resString = f"Unexpected Error: {http_error}"
                raise HTTPException(status_code=500, detail=resString)




