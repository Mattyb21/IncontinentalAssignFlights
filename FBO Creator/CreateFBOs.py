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
import csv


def print_with_timestamp(message):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_message = f"{timestamp}: {message}"
    
    # Print to console
    print(log_message)

    # Log file path (in the same directory)
    log_file_path = 'Log.txt'

    # Write to log file
    with open(log_file_path, "a") as log_file:
        log_file.write(log_message + "\n")


aaaaa = input("Press enter to start. Make sure OnAir is open")

#Click somewhere on the screen to get the window back up
pyautogui.click(x=1581, y=26)
time.sleep(1)



# Open the CSV file
with open('AirportsToCreate.csv', mode='r') as file:
    # Create a CSV reader
    reader = csv.reader(file)
    
    # Skip the header
    next(reader, None)
    
    # Loop through each row in the CSV
    for row in reader:
        # Reference the first field in the row (dpt_airport)
        airport_code = row[0]
        print_with_timestamp("Running for airport: " + airport_code)
        
        #Navigating to the airports screen
        #Click World
        pyautogui.click(x=437, y=69)
        time.sleep(1)
        #Click Airports
        pyautogui.click(x=753, y=167)
        time.sleep(5)

        #Click Aiport box
        pyautogui.click(x=94, y=252)
        time.sleep(1)

        #Type in airport
        pyautogui.write(airport_code)
        time.sleep(1)

        #click Display
        pyautogui.press('tab')
        time.sleep(1)
        pyautogui.press('tab')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(20)
        #Long wait on display
        
        #Click createFBO
        pyautogui.click(x=3732, y=303)
        time.sleep(2)
        
        #click Okay on prompt
        pyautogui.click(x=1944, y=1127)
        time.sleep(1)
        
        #actually press the okay
        pyautogui.press('enter')
        time.sleep(10)
        
        #click name of FBO
        pyautogui.click(x=548, y=285)
        time.sleep(1)
        
        #Select All
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(1)
        
        #Type new name
        pyautogui.write("INCOZ - " + airport_code)
        time.sleep(1)

        #Click get quote
        pyautogui.click(x=483, y=832)
        time.sleep(5)
        
        #Click accept
        pyautogui.click(x=520, y=552)
        time.sleep(30)

print_with_timestamp("Completed")
input("Completed")