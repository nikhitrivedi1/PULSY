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
            return False
        return True

    def _check_oura_analysis(self, response:dict) -> dict:
        # If Average HRV or HR is 0 or None -> then these are not availble
        res = defaultdict(bool)
        # Heart Rate and HRV - min and max taken on items - utilizing average as entry to proceed to others
        res['heart_rate'] = (
            response['average_heart_rate'] is not None and 
            response['average_heart_rate'] > 0 and
            'items' in response['heart_rate']
            )
        res['hrv'] = (
            response['average_hrv'] is not None and
            response['average_hrv'] > 0 and
            'items' in response['hrv']
        )

        res['movement'] = (
            response['movement_30_sec'] is not None
        )
        return res