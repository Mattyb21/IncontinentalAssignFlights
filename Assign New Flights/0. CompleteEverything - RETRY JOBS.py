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

#************* SETTINGS ***********#
PlayerJobCreationFile = 0
NoNewJobsFile = 1
CompleteEverythingFile = 0
#************* SETTINGS ***********#

script_path = 'CoreScript.py'
args = [PlayerJobCreationFile, NoNewJobsFile, CompleteEverythingFile]
command = ['python', script_path] + args
subprocess.run(command)