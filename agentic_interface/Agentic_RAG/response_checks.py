# Response Checks Class
from collections import defaultdict

class ResponseChecks:
    def __init__(self):
        pass

    def check_response(self, response:dict, endpoint_type: str, type: str = "basic") -> dict:
        """
        Check the response from the Oura API to ensure that the response is valid
        """
        if endpoint_type == "oura":
            # always execute basic check
            if not self._check_oura_basic(response):
                return {'basic': False}
            
            if type == "analysis":
                return {'basic': True, 'analysis': self._check_oura_analysis(response)}

        return {'basic': True}
    
    def _check_oura_basic(self, response:dict) -> bool:
        # If call is successful, check the response to see if data is populated
        if not response or "data" not in response or not response['data']:
            print(f"Basic check failed for response: {response}")
            return False
        return True

    def _check_oura_analysis(self, response:list) -> dict:
        # If Average HRV or HR is 0 or None -> then these are not availble
        # the response is a list of dictionaries for oura in the form of : 
        # {"data": [{"average_heart_rate": 100, "items": [100, 100, 100]}, {"average_hrv": 100, "items": [100, 100, 100]}]}
        # For the purpose of analysis right now - we will only check the first dictionary in the list
        # Since we already check the basic - we can proceed to check the analysis
        response = response['data'][0]
        res = defaultdict(bool)
        # Heart Rate and HRV - min and max taken on items - utilizing average as entry to proceed to others
        res['heart_rate'] = (
            'average_heart_rate' in response and
            response['average_heart_rate'] is not None and 
            response['average_heart_rate'] > 0 and
            'items' in response['heart_rate']
            )
        res['hrv'] = (
            'average_hrv' in response and
            response['average_hrv'] is not None and
            response['average_hrv'] > 0 and
            'items' in response['hrv']
        )

        res['movement'] = (
            'movement_30_sec' in response and
            response['movement_30_sec'] is not None
        )
        return res