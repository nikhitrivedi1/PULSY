"""
User Service Functions - Device and Goal Data Loading

Provides service-layer functions for:
- Loading wearable device metrics (sleep, stress, heart rate)
- Retrieving user goals and progress tracking
- Aggregating multi-day device data

Currently supports: Oura Ring
Planned support: Apple Watch, Fitbit

TODO: 
- Add average calculation for heart rate data
- Extend support to other wearable devices
- Add data caching for performance
"""

from DataSources.oura_data_aggregation import OuraData
from datetime import datetime, timedelta
import json
import os
from fastapi import HTTPException

# Constants
MAIN_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),"../shared/user_state.json"))

async def load_user_devices_service(device: dict) -> dict[str, str|int|float]:
    """
    Load and aggregate yesterday's metrics from a user's wearable device
    
    Fetches data from the previous day and consolidates key metrics:
    - Sleep score (0-100)
    - Stress level (hours of high stress)
    - Heart rate (BPM)
    
    Args:
        device: Dictionary containing:
            - device_type: Type of device ("Oura Ring", etc.)
            - device_name: User-assigned name
            - api_key: API access token
    
    Returns:
        dict: Consolidated metrics with keys like sleep_score, stress_score, heart_rate_data
    
    Raises:
        HTTPException: 400 if device type not supported
        HTTPException: 4xx/5xx if device API returns error
    
    TODO: Calculate average heart rate instead of using first value
    """
    device_type = device["device_type"]
    result_data = {}

    if device_type == "Oura Ring":
        # Calculate date range for yesterday's data
        start_date = datetime.today() - timedelta(days=1)
        end_date = datetime.today()
        
        # Initialize Oura Ring data aggregator
        oura_ring = OuraData(
            device["api_key"], 
            str(start_date).split(" ")[0], 
            str(end_date).split(" ")[0]
        )
        
        # Fetch all metrics from Oura API
        data_result = oura_ring.pre_load_user_data()

        # Extract individual metric categories
        sleep_data = data_result["sleep_data"]
        stress_data = data_result["stress_data"]
        heart_rate_data = data_result["heart_rate_data"]

        # Consolidate primary metrics (using most recent data point)
        if sleep_data:
            result_data["sleep_score"] = sleep_data[0]["score"]
        if stress_data:
            result_data["stress_score"] = stress_data[0]["stress_high"]
        if heart_rate_data:
            # TODO: Calculate average BPM instead of using first reading
            result_data["heart_rate_data"] = heart_rate_data[0]["bpm"]
    else:
        raise HTTPException(status_code=400, detail=f"Device type {device_type} not supported")
    
    return result_data

async def load_user_goals_service(user_id: str) -> dict[str, dict[str, str|list[dict]]]:
    """
    Retrieve user's health and fitness goals from database
    
    Goals include tracking information, evidence, and progress notes.
    Used to display goal progress in the UI.
    
    Args:
        user_id: Username/identifier for the user
    
    Returns:
        dict: User's goals with structure:
            {
                "goal_name": {
                    "description": str,
                    "start_date": str,
                    "end_date": str,
                    "evidence": [...]
                }
            }
    
    Note: Currently reads from JSON file, will migrate to PostgreSQL
    """
    with open(MAIN_DB_PATH, 'r') as file:
        user_db = json.load(file)
        return user_db[user_id]["goals"]