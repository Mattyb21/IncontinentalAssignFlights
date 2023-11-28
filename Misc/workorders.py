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
    work_order_list = [wo for wo in work_order_list if wo['Status'] == 1]
    
    for wo in work_order_list:
            print(wo['Name'])

    
except Exception as error:
    print(f"API Request Error (Get Workorders): {error}")

