import pandas as pd
import datetime
import random
import subprocess
import os
import pyautogui
import pyperclip
import requests
import json

def get_workorders(aircraft_list):
    companyId = "c1069b00-adf0-4f00-b744-4287071e5484"
    endpoint = f"https://server1.onair.company/api/v1/company/{companyId}/workorders"
    apiKey = "8e62f5f0-b026-4301-a8d8-122a2d34bd4e"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "oa-apikey": apiKey
    }

    try:
        response = requests.get(endpoint, headers=headers)
        data = json.loads(response.text)

        work_order_list = data.get('Content', [])

        # Filter work orders that contain "CREW" in the aircraft identifier
        work_order_list = [wo for wo in work_order_list if 'CREW' not in wo['Name']]

        # Create a list of identifiers of aircraft in work orders
        work_order_aircraft_list = [wo['Aircraft']['Identifier'] for wo in work_order_list]
        
    except Exception as error:
        print(f"API Request Error: {error}")

    # Remove aircraft in work_order_aircraft_list from aircraft_list
    aircraft_list = [ac for ac in aircraft_list if ac not in work_order_aircraft_list]

    endpoint = f"https://server1.onair.company/api/v1/company/{companyId}/fleet"

    try:
        response = requests.get(endpoint, headers=headers)
        data = json.loads(response.text)

        aircraft_api_list = data.get('Content', [])

        # Create a map of aircraft identifiers to current airport, hours before 100 H inspection and DisplayName
        aircraft_airport_map = {aal['Identifier']: {
            'Airport': aal.get('CurrentAirport', {}).get('ICAO', 'N/A'),
            'HoursBefore100HInspection': aal.get('HoursBefore100HInspection', 'N/A'),
            'DisplayName': aal.get('AircraftType',{}).get('DisplayName', 'N/A')
        } for aal in aircraft_api_list}

        # For each aircraft in the aircraft_list, if it exists in the aircraft_airport_map, attach the current airport, hours before 100 H inspection, and DisplayName
        aircraft_list_with_airports = [{ 
            'Aircraft': ac, 
            'Airport': aircraft_airport_map.get(ac, {}).get('Airport', 'N/A'), 
            'HoursBefore100HInspection': aircraft_airport_map.get(ac, {}).get('HoursBefore100HInspection', 'N/A'),
            'DisplayName': aircraft_airport_map.get(ac, {}).get('DisplayName', 'N/A') 
        } for ac in aircraft_list]

        return aircraft_list_with_airports

    except Exception as error:
        print(f"API Request Error: {error}")




aircraftInOperation = pd.read_csv('AircraftInOperation.csv')
aircraft_list = aircraftInOperation['Aircraft'].tolist()

aircraft_list = get_workorders(aircraft_list)
print(aircraft_list)