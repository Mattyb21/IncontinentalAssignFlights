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
from concurrent.futures import ThreadPoolExecutor, as_completed


global PlayerJobCreationFile, NoNewJobsFile, CompleteEverythingFile

#************* SETTINGS ***********#
PlayerJobCreationFile = int(sys.argv[1])
NoNewJobsFile = int(sys.argv[2])
CompleteEverythingFile = int(sys.argv[3])

# Set the path to the tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Change this to your Tesseract path

def myexcepthook(type, value, traceback, oldhook=sys.excepthook):
    oldhook(type, value, traceback)
    aaaaaaaa = input("")

sys.excepthook = myexcepthook
#************* SETTINGS ***********#


def fetch_data_for_fbo(fboId, headers):

    #Fetch jobs for a single FBO ID. Returns a tuple of the FBO ID and its missions.

    endpoint = f"https://server1.onair.company/api/v1/fbo/{fboId}/jobs"
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        return fboId, json.loads(response.text).get('Content', [])
    else:
        return fboId, []

def process_missions(fboId, missions):

    #Process the fetched missions for a given FBO ID.

    results = []
    missions_with_humanonly_true = {}
    for mission in missions:
        flights = mission.get('Charters', []) + mission.get('Cargos', [])
        for flight in flights:
            humanOnly = flight.get('HumanOnly', False)
            if humanOnly:
                missions_with_humanonly_true[mission.get("Id")] = True

        for flight in flights:
            departureAirport = flight.get('DepartureAirport', {}).get('Name', "")
            departureICAO = flight.get('DepartureAirport', {}).get('ICAO', "")
            destinationAirport = flight.get('DestinationAirport', {}).get('Name', "")
            destinationICAO = flight.get('DestinationAirport', {}).get('ICAO', "")
            distance = flight.get('Distance', "")
            if mission.get("Id") in missions_with_humanonly_true:
                humanOnly = True
            else:
                humanOnly = flight.get('HumanOnly', False)
            pay = mission.get('RealPay', "")
            expirationDate = mission.get('ExpirationDate', "")
            isLastMinute = mission.get('IsLastMinute', False)
            descript = flight.get("Description", "")
            descript = descript[:2] + descript[-1:] if descript and descript[-1:] == "n" else descript[:2]
            paxClass = int(flight.get("MinPAXSeatConf", 0))
            paxClasses = [None, None, None]
            if 0 <= paxClass <= 2:
                paxClasses[paxClass] = flight.get("PassengersNumber", "")
            cargo = flight.get("Weight", 0)

            row = [mission.get('Id', ""), fboId, departureAirport, departureICAO, destinationAirport, destinationICAO, distance, humanOnly, pay, expirationDate, isLastMinute, descript, *paxClasses, cargo]
            results.append(row)
    return results

def queryFBOJobs_parallel():
    fboIds_df = pd.read_csv('FBOs.csv')
    fboIds = fboIds_df['ID'].tolist()

    apiKey = "8e62f5f0-b026-4301-a8d8-122a2d34bd4e"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "oa-apikey": apiKey
    }

    all_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_fbo = {executor.submit(fetch_data_for_fbo, fboId, headers): fboId for fboId in fboIds}
        for future in as_completed(future_to_fbo):
            fboId, missions = future.result()
            fbo_results = process_missions(fboId, missions)
            all_results.extend(fbo_results)

    # Convert to DataFrame
    headers_list = ["Mission ID", "FBOId", "DepartureAirport", "DepartureICAO", "DestinationAirport", "DestinationICAO", "Distance", "HumanOnly", "Pay", "Expiration Date", "Is Last Minute", "Descript", "PaxClass0", "PaxClass1", "PaxClass2", "Cargo"]
    results_df = pd.DataFrame(all_results, columns=headers_list)

    # Processing DataFrame as in the original function
    results_df["PaxClass0"] = pd.to_numeric(results_df["PaxClass0"], errors="coerce").fillna(0)
    results_df["PaxClass1"] = pd.to_numeric(results_df["PaxClass1"], errors="coerce").fillna(0)
    results_df["PaxClass2"] = pd.to_numeric(results_df["PaxClass2"], errors="coerce").fillna(0)
    results_df["Cargo"] = pd.to_numeric(results_df["Cargo"], errors="coerce").fillna(0)
    results_df.loc[results_df["Cargo"] > 0, "Cargo"] = results_df.loc[results_df["Cargo"] > 0, "Cargo"] * 0.45359237

    # Assuming you want to sum duplicates based on these columns as "grouped_df" in the original function
    grouped_df = results_df.groupby(["Mission ID", "FBOId", "DepartureAirport", "DepartureICAO", "DestinationAirport", "DestinationICAO", "Distance", "HumanOnly", "Pay", "Expiration Date", "Is Last Minute", "Descript"], as_index=False).sum()

    grouped_df.to_csv('flights.csv', index=False)
    print_with_timestamp("FBO Jobs Query Complete")



def find_first_occurrence_of_word(word):
    # Take a screenshot
    screenshot = pyautogui.screenshot()

    # Use OCR to find text in the screenshot
    text_data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

    occurrence_count = 0  # Counter for the occurrences of the word

    # Look for the word in the OCR results
    for i in range(len(text_data['text'])):
        if text_data['text'][i].lower() == word.lower():
            occurrence_count += 1
            if occurrence_count == 1:  # Check if it's the second occurrence
                # Extract coordinates of the word
                x = text_data['left'][i]
                y = text_data['top'][i]
                return x, y

    return None

def find_second_occurrence_of_word(word):
    # Take a screenshot
    screenshot = pyautogui.screenshot()

    # Use OCR to find text in the screenshot
    text_data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

    occurrence_count = 0  # Counter for the occurrences of the word

    # Look for the word in the OCR results
    for i in range(len(text_data['text'])):
        if text_data['text'][i].lower() == word.lower():
            occurrence_count += 1
            if occurrence_count == 2:  # Check if it's the second occurrence
                # Extract coordinates of the word
                x = text_data['left'][i]
                y = text_data['top'][i]
                return x, y

    return None

def click_second_occurrence(word):
    coords = find_second_occurrence_of_word(word)
    if coords:
        # Move the mouse to the second occurrence of the word and click
        pyautogui.click(coords[0], coords[1])
    else:
        aaaaaaa = input(f"Second occurrence of '{word}' not found on screen.")
        print_with_timestamp(f"Second occurrence of '{word}' not found on screen.")

def click_first_occurrence(word):
    coords = find_first_occurrence_of_word(word)
    if coords:
        # Move the mouse to the second occurrence of the word and click
        pyautogui.click(coords[0], coords[1])
    else:
        print_with_timestamp(f"First occurrence of '{word}' not found on screen.")
        aaaaaaa = input(f"First occurrence of '{word}' not found on screen.")

def filter_human_only(missions, human_only):
    if human_only == 1:
        missions = missions.groupby('Mission ID').filter(lambda x: (~x['HumanOnly']).all())
    return missions

def filter_last_minute(missions, last_minute):
    if last_minute == 1:
        return missions[missions['Is Last Minute'] == False]
    return missions

def player_mixup(missions):
    # Count flights per mission
    mission_counts = missions['Mission ID'].value_counts()

    # Identify missions with more than 4 flights
    missions_to_remove = mission_counts[mission_counts > 4].index

    # Filter these missions out
    missions_filtered = missions[~missions['Mission ID'].isin(missions_to_remove)]
    return missions_filtered

def filter_pax(missions, minPax0, maxPax0, minPax1, maxPax1, minPax2, maxPax2, minCargo, maxCargo, max_range):
    def is_mission_valid(mission):
        # Check each row of a mission
        for _, row in mission.iterrows():
            pax0, pax1, pax2, cargo, distance = row['PaxClass0'], row['PaxClass1'], row['PaxClass2'], row['Cargo'], row['Distance']

            # Check if mission satisfies all constraints
            if not (minPax2 <= pax2 <= maxPax2 and
                    minPax1 <= pax1 <= (maxPax1 + maxPax2 - pax2) and
                    minPax0 <= pax0 <= (maxPax0 + (maxPax2 - pax2) + (maxPax1 - pax1)) and
                    minCargo <= cargo <= maxCargo and distance <= max_range):
                return False

        return True

    # Filter out missions if they don't satisfy all constraints
    valid_missions = missions.groupby('Mission ID').filter(is_mission_valid).reset_index(drop=True)
    
    return valid_missions
    
def filter_by_expiration(missions, hours):
    now = datetime.datetime.utcnow()
    time_delta = datetime.timedelta(hours=hours)
    future_time = now + time_delta

    # If 'Expiration Date' is not a datetime object, convert it
    if missions['Expiration Date'].dtype != 'datetime64[ns]':
        missions['Expiration Date'] = missions['Expiration Date'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%dT%H:%M:%S.%f') if '.' in x else pd.to_datetime(x, format='%Y-%m-%dT%H:%M:%S'))

    return missions[missions['Expiration Date'] >= future_time]

def find_next_mission(missions, current_icao):
    if route.empty:
        for index, mission in missions.iterrows():
            if mission['DepartureICAO'] == current_icao:
                return mission
    else:
        for index, mission in missions.iterrows():
            # Check if 'Mission ID' is not in 'route' when 'route' is not empty
            if mission['DepartureICAO'] == current_icao and mission['Mission ID'] not in route['Mission ID'].values:
                return mission

def get_mission_distance(missions, mission_id):
    mission_flights = missions[missions['Mission ID'] == mission_id]
    return mission_flights['Distance'].sum()

def count_flights_in_mission(missions, mission_id):
    # Filter the missions DataFrame to only include rows with the given mission ID
    mission_flights = missions[missions['Mission ID'] == mission_id]
    
    # Return the number of rows in the filtered DataFrame, which is the number of flights in the mission
    return len(mission_flights)

def find_mission_flights(missions, mission_id, current_icao):
    # Select all flights from the mission with the given mission_id
    mission_flights = missions[missions['Mission ID'] == mission_id]

    # Prepare an empty DataFrame to store the ordered flights
    ordered_mission_flights = pd.DataFrame()

    # Loop until all flights for this mission have been processed
    while not mission_flights.empty:

        # From the remaining flights for this mission, select the ones departing from current_icao
        available_flights = mission_flights[mission_flights['DepartureICAO'] == current_icao]

        # If there are no more flights departing from current_icao, break the loop
        if available_flights.empty:
            break


        for i in range(len(available_flights)):
            # Select the ith available flight
            potential_next_flight = available_flights.iloc[i]
            subsequent_flights = mission_flights[mission_flights['DepartureICAO'] == potential_next_flight['DestinationICAO']]

            # If there are subsequent flights from this destination, or this is the last flight in the mission, select it
            if not subsequent_flights.empty or i == len(available_flights) - 1:
                next_flight = potential_next_flight
                break

        # Add this flight to our ordered list (transforming the Series to a DataFrame with to_frame().T)
        ordered_mission_flights = pd.concat([ordered_mission_flights, next_flight.to_frame().T], ignore_index=True)

        # Remove this flight from the mission_flights DataFrame
        mission_flights = mission_flights.drop(next_flight.name)

        # Update the current_icao to the destination of the next flight, for the next iteration
        current_icao = next_flight['DestinationICAO']

    # Return the DataFrame of ordered flights
    return ordered_mission_flights

def add_flights_from_mission(missions, mission_flights, max_flights, max_Hours):

    global route, work_order    
    # Iterate over each flight in the mission
    for _, flight in mission_flights.iterrows():
        # Add the current flight to the route
        route = pd.concat([route, flight.to_frame().T], ignore_index=True)
        # Add the current flight to the work order with its details
        
        work_order = work_order.dropna(how='all', axis=1)
        
        work_order = pd.concat([work_order, pd.DataFrame({
            'Order': [len(route)],
            'Mission ID': [flight['Mission ID']],
            'DepartureICAO': [flight['DepartureICAO']],
            'DestinationICAO': [flight['DestinationICAO']],
            'Distance': [flight['Distance']],
            'Descript' : [flight['Descript']],
            'PaxClass0' : [flight['PaxClass0']],
            'PaxClass1' : [flight['PaxClass1']],
            'PaxClass2' : [flight['PaxClass2']],
            'Cargo' : [flight['Cargo']]
        })], ignore_index=True)

        # After adding a flight from the mission, remove the mission from the list of missions
        missions = missions[missions['Mission ID'] != mission_flights.iloc[0]['Mission ID']]

        # Update the current ICAO to the destination of the last added flight
        current_icao = flight['DestinationICAO']

        if current_flights != max_flights:
            dfs(missions, current_icao, max_flights, max_Hours)

    return missions, current_icao

def dfs(missions, current_icao, max_flights, max_Hours):
    global current_flights, hoursWorked, knots
    # If the total number of flights in the route reaches the maximum, stop the recursion
    if current_flights == max_flights:
        return

    # While the total flights haven't reached the maximum
    while current_flights < max_flights:
        # Find the next available mission starting from the current ICAO
        next_mission = find_next_mission(missions, current_icao)

        # If there is no next mission, end the loop
        if next_mission is None:
            break

        # Retrieve all the flights for the next mission starting from current_icao
        if current_flights != max_flights:
            mission_flights = find_mission_flights(missions, next_mission['Mission ID'], current_icao)

        # If adding all flights in this mission would exceed max_flights, skip to next mission
        if current_flights + count_flights_in_mission(missions, next_mission['Mission ID']) > max_flights or hoursWorked + ((get_mission_distance(missions, next_mission['Mission ID']) / knots) + (count_flights_in_mission(missions, next_mission['Mission ID']) * 0.6)) > max_Hours:
            missions = missions[missions['Mission ID'] != next_mission['Mission ID']]
            continue
        else:
            current_flights += count_flights_in_mission(missions, next_mission['Mission ID'])
            
            # Add the hours for the mission
            hoursWorked += (get_mission_distance(missions, next_mission['Mission ID']) / knots) + (count_flights_in_mission(missions, next_mission['Mission ID']) * 0.6)
            
            # Add the flights from the mission to the route and update the flights count and current ICAO
            missions, current_icao = add_flights_from_mission(missions, mission_flights, max_flights, max_Hours)

        # If we've reached the maximum number of flights, break the loop
        if current_flights == max_flights:
            break

def remove_selected_missions(selected_mission_ids):
    # Read the flights.csv into a DataFrame
    missions = pd.read_csv('flights.csv')

    # Remove records with Mission IDs present in the list of selected missions
    missions = missions[~missions['Mission ID'].isin(selected_mission_ids)]

    # Resave the updated DataFrame back to flights.csv
    missions.to_csv('flights.csv', index=False)

def plan_route(starting_icao, human_only, last_minute, hours, route_amount, max_Hours, playerMixup, workOrderName):
    print_with_timestamp("Beginning route planning for: " + workOrderName + " at " + starting_icao)
    
    missions = pd.read_csv('flights.csv')
    fbos = pd.read_csv('FBOs.csv')

    missions = missions.merge(fbos, left_on='FBOId', right_on='ID', how='left')
    missions = missions.drop(columns=['FBOId', 'ID', 'Airport Name', 'ICAO'])
    missions = missions.rename(columns={'FBONAME': 'FBOId'})

    missions = filter_human_only(missions, human_only)
    missions = filter_last_minute(missions, last_minute)
    missions = filter_by_expiration(missions, hours)
    missions = filter_pax(missions, minPax0, maxPax0, minPax1, maxPax1, minPax2, maxPax2, minCargo, maxCargo, max_range)
    
    if playerMixup != 1:
        missions = missions.sort_values(by='Pay', ascending=False)
    else:
        missions = player_mixup(missions)
        missions = missions.sample(frac=1)
        
    
    global route, work_order, current_flights, hoursWorked, knots, maxHours
    current_flights = 0
    route = pd.DataFrame()
    hoursWorked = 0
    work_order = pd.DataFrame(columns=['Order', 'Mission ID', 'DepartureICAO', 'DestinationICAO', 'Distance', 'Descript', 'PaxClass0', 'PaxClass1', 'PaxClass2', 'Cargo'])
    dfs(missions, starting_icao, route_amount, max_Hours)
    
    if not route.empty:
        jobs_take = pd.DataFrame()
        jobs_take = route.copy()
        jobs_take = jobs_take.groupby('Mission ID').first().reset_index()[['FBOId', 'Pay']]
        total_pay = jobs_take['Pay'].sum()
        jobs_take['Pay'] = jobs_take['Pay'].map('{:,.2f}'.format)
        jobs_take['WorkOrderName'] = workOrderName
        jobs_take = jobs_take.sort_values(by='FBOId', ascending=True)
        jobs_take['WorkOrderName'] = workOrderName

        route.to_csv('output.csv', index=False)
        #workOrderName = input('Please type the aircraft name: ').upper()

        work_order.to_csv('workorder_' + workOrderName + '.csv', index=False)
        jobs_take.to_csv('JobsToTake.csv', index=False, mode='a', header=not os.path.exists('JobsToTake.csv'))
        print_with_timestamp("Created route for " + workOrderName + ". Requested " + str(route_amount) + " flights, selected " + str(len(work_order)))
    else:
        print_with_timestamp("No flights available to create route for " + workOrderName)
    
    return work_order['Mission ID'].tolist()

def automation_flights(starting_icao, aircraftType, preset, aircraftName, playerMixup):

    global minPax0, maxPax0, minPax1 ,maxPax1, minPax2, maxPax2, minCargo, maxCargo, knots, opCost, max_range

    if aircraftType == 'Airbus A320':
        minPax0 = 155
        maxPax0 = 186
        minPax1 = 0
        maxPax1 = 0
        minPax2 = 0
        maxPax2 = 0
        minCargo = 0
        maxCargo = 0
        knots = 447
        opCost = 69559
        max_range = 1784

    if aircraftType == 'TBM 930':
        knots = 330
        minPax0 = 0
        maxPax0 = 0
        minPax1 = 0
        maxPax1 = 0
        minPax2 = 1
        maxPax2 = 4
        minCargo = 0
        maxCargo = 0
        opCost = 1395
        max_range = 3300

    if aircraftType == 'Boeing 787-10':
        minPax0 = 154
        maxPax0 = 222
        minPax1 = 42
        maxPax1 = 62
        minPax2 = 21
        maxPax2 = 31
        minCargo = 0
        maxCargo = 30000
        knots = 488
        opCost = 236034
        max_range = 5688 #Reduced for full fuel load with 315 pax
        
    if aircraftType == 'Cessna CJ4 Citation':
        minPax0 = 0
        maxPax0 = 0
        minPax1 = 0
        maxPax1 = 0
        minPax2 = 3
        maxPax2 = 8
        minCargo = 0
        maxCargo = 0
        knots = 406
        opCost = 3055
        max_range = 2165

    if aircraftType == 'Airbus A320 Neo':
        minPax0 = 155
        maxPax0 = 186
        minPax1 = 0
        maxPax1 = 0
        minPax2 = 0
        maxPax2 = 0
        minCargo = 0
        maxCargo = 0
        knots = 447
        opCost = 69559
        max_range = 1784

    last_minute = 1 #disables last minute running
    playerMixup = playerMixup

    if preset == "a":
        route_amount = 4
        hours = 22
        max_Hours = 13

    if preset == "b":
        route_amount = 8
        hours = 44
        max_Hours = 26

    if preset == "c":
        route_amount = 12
        hours = 66
        max_Hours = 39

    if preset == "d":
        route_amount = 16
        hours = 88
        max_Hours = 52

    if preset == "e":
        route_amount = 20
        hours = 110
        max_Hours = 66

    if preset == "f":
        route_amount = 24
        hours = 132
        max_Hours = 79

    if preset == "g":
        route_amount = 28
        hours = 154
    
    if PlayerJobCreationFile == 1:
        route_amount = preset
        hours = 75
        max_Hours = 100
        
    selected_mission_ids = plan_route(starting_icao, 1, last_minute, hours, route_amount, max_Hours, playerMixup, aircraftName)

    if selected_mission_ids:
        remove_selected_missions(selected_mission_ids)

def get_workorders(aircraft_list):
    #Checks current work orders and then removes aircraft that have them
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
        work_order_list = [wo for wo in work_order_list if 'CREW' not in wo['Name'] and 'Work Order' not in wo['Name']]
        #work_order_list = [wo for wo in work_order_list if wo['Status'] == 1]

        # Create a list of identifiers of aircraft in work orders
        work_order_aircraft_list = [wo['Aircraft']['Identifier'] for wo in work_order_list]
        
        print_with_timestamp("Aircraft in operation: ")
        print_with_timestamp(work_order_aircraft_list)
        
        
    except Exception as error:
        print_with_timestamp(f"API Request Error (Get Workorders): {error}")

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
        print_with_timestamp(f"API Request Error: {error}")

def queryFBOJobs():

    fboIds_df = pd.read_csv('FBOs.csv')
    fboIds = fboIds_df['ID'].tolist()

    apiKey = "8e62f5f0-b026-4301-a8d8-122a2d34bd4e"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "oa-apikey": apiKey
    }

    headers_list = ["Mission ID", "FBOId", "DepartureAirport", "DepartureICAO", "DestinationAirport", "DestinationICAO", "Distance", "HumanOnly", "Pay", "Expiration Date", "Is Last Minute", "Descript", "PaxClass0", "PaxClass1", "PaxClass2", "Cargo"]
    results = []
    groupedResults = {}
    missions_with_humanonly_true = {}
    print_with_timestamp("Beginning FBO Jobs Query")

    for fboId in fboIds:
        endpoint = "https://server1.onair.company/api/v1/fbo/" + str(fboId) + "/jobs"

        response = requests.get(endpoint, headers=headers)
        statusCode = response.status_code
        #print_with_timestamp(f"Response Status Code for FBO ID {fboId}: {statusCode}")

        if statusCode == 200:
            responseData = response.text
            if responseData:
                responseJson = json.loads(responseData)
                missions = responseJson.get('Content', [])
                
                for mission in missions:
                    flights = mission.get('Charters', []) + mission.get('Cargos', [])
                    
                    for flight in flights:
                        humanOnly = flight.get('HumanOnly', False)
                        if humanOnly:
                            missions_with_humanonly_true[mission.get("Id")] = True
                            
                    for flight in flights:
                        departureAirport = flight.get('DepartureAirport', {}).get('Name', "")
                        departureICAO = flight.get('DepartureAirport', {}).get('ICAO', "")
                        destinationAirport = flight.get('DestinationAirport', {}).get('Name', "")
                        destinationICAO = flight.get('DestinationAirport', {}).get('ICAO', "")
                        distance = flight.get('Distance', "")
                        if mission.get("Id") in missions_with_humanonly_true:
                            humanOnly = True
                        else:
                            humanOnly = flight.get('HumanOnly', False)
                        pay = mission.get('RealPay', "")
                        expirationDate = mission.get('ExpirationDate', "")
                        isLastMinute = mission.get('IsLastMinute', False)
                        descript = flight.get("Description", "")
                        if descript[-1:] == "n":
                            descript = descript[:2] + descript[-1:] if descript else ""
                        else:
                            descript = descript[:2] if descript else ""
                        paxClass = int(flight.get("MinPAXSeatConf", 0))
                        
                        paxClasses = [None, None, None]
                        if 0 <= paxClass <= 2:
                            paxClasses[paxClass] = flight.get("PassengersNumber", "")

                        key = mission.get("Id") + "_" + descript

                        if key not in groupedResults:
                            groupedResults[key] = [mission.get("Id"), fboId, departureAirport, departureICAO, destinationAirport, destinationICAO, distance, humanOnly, pay, expirationDate, isLastMinute, descript, *paxClasses]
                        else:
                            for i in range(3):
                                if paxClasses[i]:
                                    groupedResults[key][12 + i] = (groupedResults[key][12 + i] or 0) + paxClasses[i]
                        
                        row = [mission.get('Id', ""), fboId, departureAirport, departureICAO, destinationAirport, destinationICAO, distance, humanOnly, pay, expirationDate, isLastMinute, descript, *paxClasses, flight.get("Weight", 0)]
                        results.append(row)
            else:
                print_with_timestamp(f"No response data received from the API for FBO ID {fboId}")
        else:
            print_with_timestamp(f"Unexpected API response for FBO ID {fboId}: {statusCode}")

    results_df = pd.DataFrame(results, columns=headers_list)
    
    results_df["PaxClass0"] = pd.to_numeric(results_df["PaxClass0"], errors="coerce").fillna(0)
    results_df["PaxClass1"] = pd.to_numeric(results_df["PaxClass1"], errors="coerce").fillna(0)
    results_df["PaxClass2"] = pd.to_numeric(results_df["PaxClass2"], errors="coerce").fillna(0)
    results_df["Cargo"] = pd.to_numeric(results_df["Cargo"], errors="coerce").fillna(0)
    
    results_df.loc[results_df["Cargo"] > 0, "Cargo"] = results_df.loc[results_df["Cargo"] > 0, "Cargo"] * 0.45359237
    
    grouped_df = results_df.groupby(["Mission ID", "FBOId", "DepartureAirport", "DepartureICAO", "DestinationAirport", "DestinationICAO", "Distance", "HumanOnly", "Pay", "Expiration Date", "Is Last Minute", "Descript"]).sum().reset_index()

    grouped_df.to_csv('flights.csv', index=False)
    print_with_timestamp("FBO Jobs Query Complete")

def queryFBOs():
    companyId = "c1069b00-adf0-4f00-b744-4287071e5484"
    endpoint = f"https://server1.onair.company/api/v1/company/{companyId}/fbos"

    apiKey = "8e62f5f0-b026-4301-a8d8-122a2d34bd4e"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "oa-apikey": apiKey
    }

    try:
        response = requests.get(endpoint, headers=headers)
        data = json.loads(response.text)

        fboList = data.get('Content', [])

        # Prepare the table headers
        headersData = [["ID", "Airport Name", "ICAO", "FBONAME"]]

        results = headersData + [[fbo['Id'], fbo['Airport']['Name'], fbo['Airport']['ICAO'], fbo['Name']] for fbo in fboList]

        # Create a DataFrame from the results
        results_df = pd.DataFrame(results[1:], columns=results[0])

        # Write the DataFrame to a CSV file
        results_df.to_csv('FBOs.csv', index=False)
        print_with_timestamp("FBO's retrieved")
    except Exception as error:
        print_with_timestamp(f"API Request Error: {error}")

def aircraftmaintenance(aircraft_List):
    # We will insert the aircraft maintenance part here
    aircraft_names = [entry['Aircraft'] for entry in aircraft_List]
    time.sleep(20)
    
    # Sort by engine
    pyautogui.click(x=2092, y=305)
    time.sleep(2)

    # Click first row
    pyautogui.click(x=1760, y=347)
    time.sleep(1)

    # Copy data from first row
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1.5)
    ac_maint_line = pyperclip.paste().split("\t")
    time.sleep(1)
    maint_variable = 347
    # 40 pixels per row

    while True:

        if 'Needed' not in ac_maint_line[3]:
            if float(ac_maint_line[14].split()[0]) > 0.70 and float(ac_maint_line[10].split()[0]) > 35:
                break
        
        if ac_maint_line[0] in aircraft_names and 'Needed' not in ac_maint_line[4]:
            # Do maintenance
            # Select Manage
            print_with_timestamp("Doing maintenance on " + ac_maint_line[0])
            pyautogui.click(x=720, y=maint_variable)
            time.sleep(1)
            
            # Select Workshop
            pyautogui.click(x=1050, y=maint_variable + 116)
            time.sleep(15)
            
            
            # Select 100h or annual
            if float(ac_maint_line[11]) < 8:
                print_with_timestamp(ac_maint_line[0] + " requires annual inspection")
                #Select annual
                pyautogui.click(x=662, y=800)
                time.sleep(1)
            else:
                #Select 100h
                pyautogui.click(x=662, y=843)
                time.sleep(1)
            
            # Repair Airframe
            pyautogui.click(x=718, y=972)
            time.sleep(1)
            
            # Engine 1
            pyautogui.click(x=1094, y=1045)
            time.sleep(1)
            
            # Engine 2
            pyautogui.click(x=1094, y=1078)
            time.sleep(1)
            
            # Airframe Cond
            pyautogui.click(x=1020, y=967)
            time.sleep(1)
            pyautogui.write('99')
            time.sleep(1)
            
            # E1 cond
            pyautogui.click(x=726, y=1045)
            time.sleep(1)
            pyautogui.write('99')
            time.sleep(1)
            
            # E2 cond
            pyautogui.click(x=726, y=1078)
            time.sleep(1)
            pyautogui.write('99')
            time.sleep(1)
            
            # Dropdown Box for FBO
            pyautogui.click(x=2790, y=326)
            time.sleep(1)
            
            # Use image recog to find it
            click_second_occurrence('INCOZ')

            # Get quote
            pyautogui.click(x=3204, y=323)
            time.sleep(2)

            if float(ac_maint_line[11]) < 8:
                #Select Pay and Start (A bit lower because annual inspection)
                pyautogui.click(x=3124, y=655)
                time.sleep(40)
            else:
                #Select Pay and Start
                pyautogui.click(x=3124, y=611)
                time.sleep(40)
            
            # Sort by Engines
            pyautogui.click(x=2092, y=305)
            time.sleep(1)

        maint_variable += 42

        # Click on next row
        pyautogui.click(x=1760, y=maint_variable)
        time.sleep(1)
 
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(1.5)
        ac_maint_line = pyperclip.paste().split("\t")
        time.sleep(1)

def LaunchandPrepOnair():

    #We will insert launch info here:

    # Launch the application
    onair_appref_ms_path = r'C:\Users\Server\Desktop\OnAir Company.appref-ms'
    subprocess.Popen(f'cmd /c start "" "{onair_appref_ms_path}"', shell=True)

    # Wait for a moment to allow the application to start
    time.sleep(10)

    # Try to find the window
    try:
        # You need to know the title of the window to find it
        window_title = "OnAir Airline Manager" 
        onair_window = gw.getWindowsWithTitle(window_title)[0]  # Get the first window with the title

        if onair_window:
            # Maximize the window
            onair_window.maximize()
            print_with_timestamp("Window maximized.")
        else:
            print_with_timestamp("Window not found.")
    except Exception as e:
        print_with_timestamp(f"An error occurred: {e}")

    time.sleep(20)


    #Click Resume
    pyautogui.click(x=2231, y=1573)
    time.sleep(45)

    #Click VA Ops
    pyautogui.click(x=627, y=55)
    time.sleep(1)

    #Click VA
    pyautogui.click(x=627, y=175)
    time.sleep(60)
    #Real wake up call that onair is slow as fuck

# Try to find the window
    try:
        # You need to know the title of the window to find it
        window_title = "OnAir VA Management Console" 
        onair_window = gw.getWindowsWithTitle(window_title)[0]  # Get the first window with the title

        if onair_window:
            # Maximize the window
            onair_window.maximize()
            print_with_timestamp("Window maximized.")
        else:
            print_with_timestamp("Window not found.")
    except Exception as e:
        print_with_timestamp(f"An error occurred: {e}")

    time.sleep(1)
    
    #Click Aircaft Selection
    #pyautogui.click(x=1820, y=63)
    #Doing this through hotkey now
    pyautogui.hotkey('alt', 'a')
    time.sleep(25)

def screenshot_fbo_job(word):
    # Take a screenshot
    screenshot = pyautogui.screenshot()

    # Use OCR to find text in the screenshot
    text_data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

    occurrence_count = 0  # Counter for the occurrences of the word

    # Look for the word in the OCR results
    for i in range(len(text_data['text'])):
        if text_data['text'][i].lower() == word.lower():
            occurrence_count += 1
            if occurrence_count == 1:
                # Extract coordinates of the word
                x = text_data['left'][i]
                y = text_data['top'][i]
                return y
    
    y = 0
    return y

def take_queries():

    #Navigate to the queries page
    time.sleep(1)
    #Hotkeying to the pending page
    pyautogui.hotkey('alt', 'p')
    time.sleep(20)
    
    #Navigate to the FBO queries page
    pyautogui.click(x=843, y=231)
    time.sleep(25)

    # Load the JobsToTake.csv file into a DataFrame
    jobs_df = pd.read_csv('JobsToTake.csv')

    # Load the FBOs.csv file into a DataFrame
    fbos_df = pd.read_csv('FBOs.csv')

    # Get the values in the first field (field 0) from the JobsToTake.csv file
    jobs_FBOID = set(jobs_df.iloc[:, 0].values)
    
    #Sort by Exp
    pyautogui.click(x=1000, y=423)
    time.sleep(1)
    
    #sort descending
    pyautogui.click(x=1000, y=423)
    time.sleep(1)
    

    #Clicking Select FBO
    pyautogui.click(x=243, y=300)
    time.sleep(1)

    # Go through each record in the fourth field (field 3) of the FBOs.csv file
    for index, row in fbos_df.iterrows():
        FBOs = row.iloc[3]  # Access the value in the fourth field (field 3)

        # Check if the value exists in the first field (field 0) of the JobsToTake.csv file
        if FBOs in jobs_FBOID:
            #Select the FBO
            pyautogui.sleep(1)
            pyautogui.press('enter')

            jobs_Amount = 0
            jobs_Amount_Taken = 0
            # Check each row in JobsToTake.csv to see if the FBO matches
            for job_index, job_row in jobs_df.iterrows():
                if job_row.iloc[0] == FBOs:
                    jobs_Amount += 1

            print_with_timestamp("Searching " + FBOs + " for " + str(jobs_Amount) + " jobs.")
            #Wait ages for it to load
            pyautogui.sleep(60)
            
            #We are going to do some image reco shit

            #the X value of the take button
            
            fuckedLoop = 0

            while fuckedLoop < 300:
                for job_index, job_row in jobs_df.iterrows():
                    if job_row.iloc[0] == FBOs:
                        #finding the $ value on the screen
                        #print_with_timestamp('Searching for ' + str(job_row.iloc[1]))
                        query_y_value = screenshot_fbo_job(job_row.iloc[1])
                        #print_with_timestamp('y value: ' + str(query_y_value))
                        if query_y_value < 1:
                            #Click a different entry and retry - first line
                            pyautogui.click(x=646, y=469)
                            time.sleep(1)
                            query_y_value = screenshot_fbo_job(job_row.iloc[1])
                            if query_y_value < 1:
                                #Click a different entry and retry - second line
                                pyautogui.click(x=740, y=505)
                                time.sleep(1)
                                query_y_value = screenshot_fbo_job(job_row.iloc[1])
                                if query_y_value < 1: #Just going to retry the search, seems like the font in white throws the screengrab
                                    print_with_timestamp('Couldnt find job on screen, searched for: ' + str(job_row.iloc[1]))
                                    aaaaaa = input('Couldnt find job on screen, searched for: ' + str(job_row.iloc[1]))
                                    pyautogui.click(x=1000, y=10)
                                
                                
                        pyautogui.click(x=107, y=query_y_value)
                        #print_with_timestamp('Mouse would be clicking right now')
                        time.sleep(5)
                        #print_with_timestamp('End')
                        jobs_Amount_Taken += 1
                        query_y_value = 0
                        time.sleep(5)
                        
                if jobs_Amount_Taken == jobs_Amount:
                    pyautogui.click(x=243, y=300)
                    pyautogui.sleep(0.5)
                    #Found all the jobs for this FBO
                    break
        #Next FBO
        pyautogui.press('down')
        pyautogui.sleep(0.5)

def createWorkOrder(aircraft, workOrderName, listLocation):

    #Aircraft is aircraft type
    #workOrderName is VH-XXX
    #List Location is where it is in the select aircraft list
    #31 pixels * listLocation
    load_fuel = 1
    rest_crew = 1
    print_with_timestamp("Creating a workorder for " + workOrderName)

    #Select All Aircraft
    time.sleep(1)
    pyautogui.click(x=259, y=329)
    time.sleep(1)

    #Select Top Aircraft
    pyautogui.click(x=229, y=402)
    time.sleep(1)
    
    #Select the right plane, starting at the first one, 30 pixels between each one
    while listLocation > 0:
        pyautogui.press("down")
        time.sleep(0.1)
        listLocation = listLocation - 1

    #listLocation = 318 + (listLocation * 31.25)
    #pyautogui.click(x=315, y=listLocation)
    #time.sleep(1)
    
    
    #Select Copy Crew
    pyautogui.click(x=451, y=1186)
    time.sleep(1)
    
    #Select Work Order Name
    pyautogui.doubleClick(x=49, y=180)
    pyautogui.sleep(0.5)
    pyautogui.hotkey('ctrl', 'c')
    pyautogui.sleep(1.5)

    #Starting the crew off with 0 hours
    hoursWorked = 0

    pyautogui.hotkey('ctrl', 'a')
    pyautogui.write(workOrderName)
    
    original_departure = 0

    with open('workorder_' + workOrderName + '.csv', 'r') as file:
        lines = file.readlines()
        lines = lines[1:]
        #Skipping header
        #next(file)

        for i in range(len(lines)):
            # Split the line into fields (assuming comma separated values)
            
            line = lines[i]
            fields = line.strip().split(',')

            # Extract the relevant information
            origin = fields[2]
            destination = fields[3]
            distance = int(round(float(fields[4])))
            descript = fields[5]
            
            
            #Entering original departure, do one off tasks
            if original_departure == 0:
                pyautogui.click(x=87, y=417)
                time.sleep(0.5)
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.5)
                pyautogui.write(origin)
                time.sleep(0.5)
                #Select Legs
                pyautogui.click(x=385, y=236)
                time.sleep(1)
                #Delete Grouped By
                pyautogui.click(x=854, y=810)
                time.sleep(0.5)
                
                original_departure = 1
            
            #Enter the dest icao
            pyautogui.click(x=619, y=346)
            pyautogui.sleep(0.2)
            pyautogui.write(destination)
            
            
            
            
            #Starting line for first payload. We add 33 for each payload we go down        
            pyautogui.click(x=1079, y=885)
            pyautogui.sleep(0.2)
            
            pyautogui.hotkey('ctrl', 'c')
            pyautogui.sleep(0.2)
            
            currentPayload = pyperclip.paste().split("\t")
            pyautogui.sleep(0.2)
            
            #Tab across to the load box
            pyautogui.press('tab')
            pyautogui.sleep(0.1)
            pyautogui.press('tab')
            pyautogui.sleep(0.1)
            pyautogui.press('tab')
            pyautogui.sleep(0.1)
            pyautogui.press('tab')
            pyautogui.sleep(0.1)
            pyautogui.press('tab')
            pyautogui.sleep(0.1)
            pyautogui.press('tab')
            pyautogui.sleep(0.1)
            
            
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.2)
            currentPayload = pyperclip.paste().split("\t")
            
            comparisonPasteVariable = 0
            entireRetryVariable = 0
            fuckedLoop = 0
            #Setting to check we look at the type before we load
            if aircraft == 'Airbus A320':
                ecoPaxLoaded = 0
                busPaxLoaded = 1
                firstPaxLoaded = 1
                cargoLoaded = 1
                
            if aircraft == 'Boeing 787-10':
                ecoPaxLoaded = 0
                busPaxLoaded = 0
                firstPaxLoaded = 0
                cargoLoaded = 0
            
            if aircraft == 'Cessna CJ4 Citation':
                ecoPaxLoaded = 1
                busPaxLoaded = 1
                firstPaxLoaded = 0
                cargoLoaded = 1
            
            #This is how many times we retry the work order
            workOrderRunFails = 0
        
            while fuckedLoop < 10000:
                #print_with_timestamp("-")
                #print_with_timestamp(currentPayload[1] + " - " + str(len(currentPayload[11])) + " - " + currentPayload[12] + " - " + str(len(currentPayload[13])) + " - " + currentPayload[3][:2] + currentPayload[3][-1:] + " - " + currentPayload[3][:2] + " - " + currentPayload[3][-1:])
                
                #Check to see if the current record matches
                if currentPayload[1] == destination and len(currentPayload[11]) == 0 and currentPayload[12] == 'False' and len(currentPayload[13]) < 4 and descript == currentPayload[3][:2] + currentPayload[3][-1:] or currentPayload[1] == destination and len(currentPayload[11]) == 0 and currentPayload[12] == 'False' and len(currentPayload[13]) < 4 and descript == currentPayload[3][:2] and currentPayload[3][-1:] != "n":
                #print_with_timestamp('currentPayload[12] = ' + str(currentPayload[12]))
            
                    if "Eco" in currentPayload[3] and ecoPaxLoaded == 0:
                        pyautogui.press('tab')
                        pyautogui.sleep(0.2)
                        pyautogui.press('space')
                        pyautogui.sleep(0.2)
                        ecoPaxLoaded = 1

                    if "Bus" in currentPayload[3] and busPaxLoaded == 0:
                        pyautogui.press('tab')
                        pyautogui.sleep(0.2)
                        pyautogui.press('space')
                        pyautogui.sleep(0.2)
                        busPaxLoaded = 1
                    
                    if "First" in currentPayload[3] and firstPaxLoaded == 0:
                        pyautogui.press('tab')
                        pyautogui.sleep(0.2)
                        pyautogui.press('space')
                        pyautogui.sleep(0.2)
                        firstPaxLoaded = 1
                        
                    if "Cargo" in currentPayload[3] and cargoLoaded == 0:
                        pyautogui.press('tab')
                        pyautogui.sleep(0.2)
                        pyautogui.press('space')
                        pyautogui.sleep(0.2)
                        cargoLoaded = 1

                if ecoPaxLoaded == 1 and busPaxLoaded == 1 and firstPaxLoaded == 1 and cargoLoaded == 1:
                    break

                if entireRetryVariable == 1: #This should be the rerun
                    print_with_timestamp(str(currentPayload[1]) + " | " + str(currentPayload[11]) + " | " + str(currentPayload[12]) + " | " + str(currentPayload[13]) + " | " + str(currentPayload[3]))

                #currentPayload[1] != destination or len(currentPayload[11]) > 0 or currentPayload[12] != 'False' or len(currentPayload[13]) > 2:
                pyautogui.press('down')
                pyautogui.sleep(0.2)
                
                #Copy Next Row
                pyautogui.hotkey('ctrl', 'c')
                time.sleep(0.2)
                
                if pyperclip.paste().split("\t") == currentPayload: #There's probably no more jobs, time to move to the next job
                    if comparisonPasteVariable < 5:
                        pyautogui.press('down')
                        pyautogui.sleep(0.2)
                        
                        #Copy Next Row
                        pyautogui.hotkey('ctrl', 'c')
                        time.sleep(0.2)
                        comparisonPasteVariable += 1
                    else:
                        if ecoPaxLoaded == 0 or busPaxLoaded == 0 or firstPaxLoaded == 0:
                            if entireRetryVariable == 1: #She's just fucked
                                break
                            
                            #redoing all the top instructions again
                            pyautogui.click(x=1079, y=885)
                            pyautogui.sleep(0.2)
                            
                            pyautogui.hotkey('ctrl', 'c')
                            pyautogui.sleep(0.2)
                            
                            currentPayload = pyperclip.paste().split("\t")
                            pyautogui.sleep(0.2)
                            
                            #Tab across to the load box
                            pyautogui.press('tab')
                            pyautogui.sleep(0.1)
                            pyautogui.press('tab')
                            pyautogui.sleep(0.1)
                            pyautogui.press('tab')
                            pyautogui.sleep(0.1)
                            pyautogui.press('tab')
                            pyautogui.sleep(0.1)
                            pyautogui.press('tab')
                            pyautogui.sleep(0.1)
                            pyautogui.press('tab')
                            pyautogui.sleep(0.1)
                            
                            
                            pyautogui.hotkey('ctrl', 'c')
                            time.sleep(0.2)
                            currentPayload = pyperclip.paste().split("\t")
                            entireRetryVariable = 1
                            comparisonPasteVariable = 0
                            print_with_timestamp("Looking for " + origin + " -> " + destination + " | " + descript + " | E / B / F: " + str(ecoPaxLoaded) + str(busPaxLoaded) + str(firstPaxLoaded))
                        else:
                            break

                currentPayload = pyperclip.paste().split("\t")
                fuckedLoop += 1
                if fuckedLoop == 200:
                    print_with_timestamp('Probably no job available that matches the destination airport')
                    exit()           

            #We should have loaded all the jobs now
            
            if ecoPaxLoaded == 0 or busPaxLoaded == 0 or firstPaxLoaded == 0:
                print_with_timestamp("Looking for " + origin + " -> " + destination + " | " + descript + " | E / B / F: " + str(ecoPaxLoaded) + str(busPaxLoaded) + str(firstPaxLoaded))
                aaaaa = input('Good chance job is fucked, we missed some pax - hit enter to proceed')
                pyautogui.click(x=1000, y=10)

            fuckedLoop = 0
            ecoPaxLoaded = 0
            busPaxLoaded = 0
            firstPaxLoaded = 0
            cargoLoaded = 0
            if aircraft == 'Airbus A320':
                ffph = 847
                knots = 447
                
            if aircraft == 'TBM9':
                ffph = 54
                knots = 330
                
            if aircraft == 'Boeing 787-10':
                ffph = 2534
                knots = 488
                
            if aircraft == 'Cessna CJ4 Citation':
                ffph = 2534
                knots = 402

            #Set Fuel
            # if load_fuel == 1:
                            
                # #The formula for A320 we use is ((Distance / Knots) * Fuel Flow Per hour) + Fuel flow per hour, with the addition being 1 hour of reserve.    
                # fuel = round(((distance / knots) * ffph) + ffph)
                
                # pyautogui.click(x=1246, y=519)
                # pyautogui.sleep(0.1)
                # pyautogui.write(str(fuel))
                # pyautogui.sleep(0.1)
            # else:
                # #Select don't load fuel
                # pyautogui.click(x=600, y=554)
            
            if int(sys.argv[1]) == 1: #If playercreationfile
                #Select no fuel operation
                pyautogui.click(x=590, y=702)

            #Set whether crew sleep
            # Divide the flight distance by the speed and then add 36 minutes of mucking about
            hoursWorked += (distance / knots) + 0.6
            #print_with_timestamp('Current hours worked:' + str(round(hoursWorked, 1)))

            
            if i+1 < len(lines):
                # get the distance for the next job
                next_distance = int(round(float(lines[i+1].strip().split(',')[4])))
                next_hours = (next_distance / knots) + 0.6
                #print_with_timestamp('Next flight hours: ' + str(next_hours))
                #print_with_timestamp('Predicted next flight hours: ' + str(next_hours + hoursWorked))
            else:
                next_hours = 14 #To force a crew rest before starting the new work order.

            if hoursWorked + next_hours > 13 and rest_crew == 1 and int(sys.argv[1]) == 0: #last check is if it's playercreationfile
                hoursWorked = 0
                pyautogui.click(x=702, y=313)



            # If hours worked is over 11 (which gives a 2 hour gap of fucking about) then rest the crew
            #if hoursWorked > 11 and rest_crew == 1:
            #    hoursWorked = 0
            #    pyautogui.click(x=1917, y=550)

            #Add a new leg
            pyautogui.click(x=121, y=285)
            pyautogui.sleep(0.2)

    #Select Delete Leg
    pyautogui.click(x=242, y=286)
    pyautogui.sleep(1)

    #Select box
    pyautogui.click(x=1954, y=1140)
    pyautogui.sleep(2)
    pyautogui.press('enter')
    pyautogui.sleep(1)

    if PlayerJobCreationFile == 0:
        #Select Activate
        pyautogui.click(x=3464, y=237)
        pyautogui.sleep(10)
    else:
        # We activate now from March update
        pyautogui.click(x=3464, y=237)
        pyautogui.sleep(10)

def workOrder_controller():
    #We will make all the workorders from here, because it's stupid how hard it is to make :(
    
    #Navigate to the workorder page
    
    #Extended time on this to allow whatever shit keeps fucking up
    time.sleep(60)
    
    
    #pyautogui.click(x=150, y=70)
    #time.sleep(5)
    
    #Click the menu
    #pyautogui.click(x=150, y=290)
    #time.sleep(40)
    #waiting for onair to load the workorder page
    
    #Hotkey to get to work orders
    pyautogui.hotkey('alt', 'w')
    time.sleep(1)
    pyautogui.hotkey('alt', 'w')
    time.sleep(1)
    pyautogui.hotkey('alt', 'w')
    time.sleep(40)
    
    #build aircraft list
    fleetList = [file for file in os.listdir('.') if file.startswith('workorder_')]
    fleetList = [filename.replace('workorder_', '').replace('.csv', '') for filename in fleetList]

    # Read the CSV file
    df = pd.read_csv('fleet.csv')

    # Iterate over each item in fleetList
    for item in fleetList:
        # Find the rows where the identifier matches the item
        matching_rows = df[df['Identifier'] == item]
        
        # Call createworkorder for each matching row
        for index, row in matching_rows.iterrows():
            #Refresh the page
            pyautogui.click(x=148, y=124)
            time.sleep(40)
            
            #print_with_timestamp("Attempting to create " + row['Identifier'])
            #Click add work order
            pyautogui.click(x=1402, y=184)
            time.sleep(5)
            createWorkOrder(row['Aircraft Type'], row['Identifier'], index) 

def queryFleet():
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
        print_with_timestamp("Fleet data retrieved and sorted")
    except Exception as error:
        print_with_timestamp(f"API Request Error: {error}")
        input("Stopped")

def RefuelFBOs():
    time.sleep(30)
    
    pyautogui.click(x=150, y=50)
    time.sleep(1)
    
    #Click the menu (MY FBOs)
    pyautogui.click(x=150, y=480)
    time.sleep(20)
    
    #Click refuel
    pyautogui.click(x=2119, y=177)
    time.sleep(20)
    
    #Click the popup box
    pyautogui.click(x=1890, y=1084)
    time.sleep(20)
    
    #Press okay - commented so we can see when the operation is done
    #pyautogui.press('enter')
    #pyautogui.sleep(1)
    
def find_aircraft_type(identifier):
    file_path = 'fleet.csv'
    fleet_df = pd.read_csv(file_path)
    matched_row = fleet_df[fleet_df["Identifier"] == identifier]
    if not matched_row.empty:
        return matched_row["Aircraft Type"].iloc[0]
    else:
        aaaaa = input("Please recheck the aircraft identifier: ")
        return "Aircraft not found in fleet"    

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

if PlayerJobCreationFile == 1:
    player_selected_aircraft = input("Enter the registration of the aircraft you're flying: ").upper()
    player_flight_amount = int(input("Enter the maximum amount of flights you would like to do: "))
    player_starting_airport = input("Enter the ICAO of the airport you are starting at, e.g. YSSY: ").upper()
    playerMixup = int(input("Type 1 to enable player mixup: "))

if PlayerJobCreationFile == 1:
    print_with_timestamp("****** Running Player Job Creation File ******")

if NoNewJobsFile == 1:
    print_with_timestamp("****** Running Job Retry File ******")

if CompleteEverythingFile == 1:
    print_with_timestamp("****** Running AI Job File ******")

print_with_timestamp("Launching OnAir")
LaunchandPrepOnair()
print_with_timestamp("Onair Prepped and Launched")


if NoNewJobsFile == 0:
    if os.path.exists('JobsToTake.csv'):
        # Get the current date for the datestamp
        datestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        new_file_name = f"JobsToTake_{datestamp}.csv"

        # Move and rename the file
        shutil.move('JobsToTake.csv', os.path.join('jobshistory', new_file_name))

        file_list = os.listdir()
        for file_name in file_list:
            if file_name.startswith('workorder_'):
                # Generate a datestamp
                datestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
                
                # Create a new filename with the datestamp
                new_file_name = f"{file_name.split('.')[0]}_{datestamp}.{file_name.split('.')[-1]}"
                
                # Move the file to workorderhistory folder with the new name
                shutil.move(file_name, os.path.join('workorderhistory', new_file_name))


aircraftInOperation = pd.read_csv('AircraftInOperation.csv')
aircraft_List = aircraftInOperation['Aircraft'].tolist()
aircraft_List = get_workorders(aircraft_List)

if NoNewJobsFile == 0 and PlayerJobCreationFile == 0:
    aircraftmaintenance(aircraft_List)
    print_with_timestamp("Aircraft Maintenance Complete")


#Query FBO's and Jobs
queryFBOs()
print_with_timestamp("FBO Query Complete")


checkForQueries = 0


if CompleteEverythingFile == 1: #We are just running the below if it's not for a player
    #We will check if we need to check the queries
    queryFleet()
    for aircraft_info in aircraft_List:
        hours_before_inspection = aircraft_info['HoursBefore100HInspection']
        if hours_before_inspection != 'N/A':  # Ensure the data exists
            hours_before_inspection = float(hours_before_inspection)  # Convert to float if necessary
            if hours_before_inspection >= 35 :
                checkForQueries = 1

    if checkForQueries == 1:
        print_with_timestamp("Aircraft in need of jobs, beginning FBO Job Query")
        #queryFBOJobs() #OLD VERSION
        queryFBOJobs_parallel()
        print_with_timestamp("FBO Job Query Complete")
    else:
        print_with_timestamp("All aircraft in operation, searching for jobs not required")

    for aircraft_info in aircraft_List:
        hours_before_inspection = aircraft_info['HoursBefore100HInspection']
        if hours_before_inspection != 'N/A':  # Ensure the data exists
            hours_before_inspection = float(hours_before_inspection)  # Convert to float if necessary
            if 52 <= hours_before_inspection:
                preset = "d"
            elif 39 <= hours_before_inspection < 52:
                preset = "c"
            elif 35 <= hours_before_inspection < 39:
                preset = "b"
            
            if hours_before_inspection >= 35:  # Aircraft doesn't need maintenance
                automation_flights(aircraft_info['Airport'], aircraft_info['DisplayName'], preset, aircraft_info['Aircraft'], 0)
                #print_with_timestamp("Route created for " + aircraft_info['Aircraft'])
            else:
                print_with_timestamp(aircraft_info['Aircraft'] + " in maintenance")

if PlayerJobCreationFile == 1:
    queryFBOJobs()
    queryFleet()
    automation_flights(player_starting_airport, find_aircraft_type(player_selected_aircraft), player_flight_amount, player_selected_aircraft, playerMixup)


file_name_jobs = 'JobsToTake.csv'

time.sleep(1)

#print_with_timestamp("Halted prior to take query") #TESTING
#input() #TESTING

if os.path.exists(file_name_jobs) and NoNewJobsFile == 0:
    print_with_timestamp("Beginning query search")
    take_queries()
    time.sleep(1)
    #Click to get rid of the dialog box
    pyautogui.click(x=1394, y=20)

if os.path.exists(file_name_jobs):
    time.sleep(1)
    print_with_timestamp("Beginning fleet search")
    queryFleet()
    time.sleep(1)
    print_with_timestamp("Beginning Work Order creation")
    workOrder_controller()

if PlayerJobCreationFile == 0:
    print_with_timestamp("Refuelling FBO's")
    RefuelFBOs()

print_with_timestamp("Process complete")
time.sleep(2)

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
# Define the old and new file paths
old_file_path = 'Log.txt'
new_file_name = f"Log_{timestamp}.txt"
new_file_path = os.path.join('logs', new_file_name)

# Ensure the 'logs' directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Move and rename the log file
shutil.move(old_file_path, new_file_path)


if os.path.exists('JobsToTake.csv'):
    # Get the current date for the datestamp
    datestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    new_file_name = f"JobsToTake_{datestamp}.csv"

    # Move and rename the file
    shutil.move('JobsToTake.csv', os.path.join('jobshistory', new_file_name))

    file_list = os.listdir()
    for file_name in file_list:
        if file_name.startswith('workorder_'):
            # Generate a datestamp
            datestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            
            # Create a new filename with the datestamp
            new_file_name = f"{file_name.split('.')[0]}_{datestamp}.{file_name.split('.')[-1]}"
            
            # Move the file to workorderhistory folder with the new name
            shutil.move(file_name, os.path.join('workorderhistory', new_file_name))


aaaaa = input('Press Enter to finish...')
