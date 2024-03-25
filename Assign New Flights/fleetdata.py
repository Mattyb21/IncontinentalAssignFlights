import pandas as pd
import datetime
import random
import subprocess
import os
import pyautogui
import pyperclip
import requests
import json
import time
import pygetwindow as gw
import shutil
import sys
import pytesseract
from PIL import Image


companyId = "c1069b00-adf0-4f00-b744-4287071e5484"
endpoint = f"https://server1.onair.company/api/v1/company/{companyId}/fleet"
apiKey = "8e62f5f0-b026-4301-a8d8-122a2d34bd4e"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "oa-apikey": apiKey
}

try:
    response = requests.get(endpoint, headers=headers)
    data = response.json()  # More direct way to get JSON response

    fleetList = data.get('Content', [])

    # Corrected list comprehension
    fleetData = [
        [
            item['Identifier'], 
            item['AircraftType']['DisplayName'], 
            item['ConfigFirstSeats'], 
            item['ConfigBusSeats'], 
            item['ConfigEcoSeats'],
            item['AircraftType']['maximumRangeInNM'], 
            item['AircraftType']['emptyWeight'], 
            item['AircraftType']['maximumGrossWeight'], 
            item['AircraftType']['FuelTotalCapacityInGallons']
        ] for item in fleetList
    ]

    # Sort by Identifier
    fleetData.sort(key=lambda x: x[0])

    # Headers corrected for consistency
    headersData = ["Identifier", "Aircraft Type", "First Seats", "Business Seats", "Economy Seats", "Maximum Range (NM)", "Empty Weight", "Maximum Gross Weight", "Fuel Capacity (Gallons)"]

    # Directly creating DataFrame
    results_df = pd.DataFrame(fleetData, columns=headersData)

    # Write the DataFrame to a CSV file
    results_df.to_csv('Fleet.csv', index=False)
    print("Fleet data retrieved and sorted")
except Exception as error:
    print(f"API Request Error: {error}")
    input("Stopped")
