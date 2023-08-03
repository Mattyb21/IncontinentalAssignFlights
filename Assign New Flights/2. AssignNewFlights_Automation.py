import pandas as pd
import datetime
import random
import subprocess
import os
import pyautogui
import pyperclip
import requests
import json

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
    print(missions_filtered)
    return missions_filtered

def filter_pax(missions, minPax0, maxPax0, minPax1, maxPax1, minPax2, maxPax2, minCargo, maxCargo):
    def is_mission_valid(mission):
        # Check each row of a mission
        for _, row in mission.iterrows():
            pax0, pax1, pax2, cargo = row['PaxClass0'], row['PaxClass1'], row['PaxClass2'], row['Cargo']

            # Check if mission satisfies all constraints
            if not (minPax2 <= pax2 <= maxPax2 and
                    minPax1 <= pax1 <= (maxPax1 + maxPax2 - pax2) and
                    minPax0 <= pax0 <= (maxPax0 + (maxPax2 - pax2) + (maxPax1 - pax1)) and
                    minCargo <= cargo <= maxCargo):
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
    for index, mission in missions.iterrows():
        if mission['DepartureICAO'] == current_icao:
            
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
    print('All flights in mission:')
    print(mission_flights[['Mission ID', 'DepartureICAO', 'DestinationICAO']])

    # Prepare an empty DataFrame to store the ordered flights
    ordered_mission_flights = pd.DataFrame()

    # Loop until all flights for this mission have been processed
    while not mission_flights.empty:

        # From the remaining flights for this mission, select the ones departing from current_icao
        available_flights = mission_flights[mission_flights['DepartureICAO'] == current_icao]

        # If there are no more flights departing from current_icao, break the loop
        if available_flights.empty:
            print('Breaking with this in mission_flights')
            print('Current ICAO: ' + current_icao)
            print(mission_flights[['Mission ID', 'DepartureICAO', 'DestinationICAO']])
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
    print('Starting Addflights')

    
    # Iterate over each flight in the mission
    for _, flight in mission_flights.iterrows():
        print('Adding flight: ' + str([flight['DepartureICAO']]) + '->' + str([flight['DestinationICAO']]))
        # Add the current flight to the route
        route = pd.concat([route, flight.to_frame().T], ignore_index=True)
        # Add the current flight to the work order with its details
        work_order = pd.concat([work_order, pd.DataFrame({
            'Order': [len(route)],
            'Mission ID': [flight['Mission ID']],
            'DepartureICAO': [flight['DepartureICAO']],
            'DestinationICAO': [flight['DestinationICAO']],
            'Distance': [flight['Distance']],
            'Descript' : [flight['Descript']]
        })], ignore_index=True)

        # After adding a flight from the mission, remove the mission from the list of missions
        missions = missions[missions['Mission ID'] != mission_flights.iloc[0]['Mission ID']]

        # Update the current ICAO to the destination of the last added flight
        current_icao = flight['DestinationICAO']
        print('Set the ICAO to ' + flight['DestinationICAO'])

        if current_flights != max_flights:
            dfs(missions, current_icao, max_flights, max_Hours)

    return missions, current_icao

def dfs(missions, current_icao, max_flights, max_Hours):
    global current_flights, hoursWorked, knots
    # If the total number of flights in the route reaches the maximum, stop the recursion
    print(f"Starting DFS - Current flights: {current_flights}, Maximum flights: {max_flights}")  # Added print
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
            print('Selected mission with ' + str(count_flights_in_mission(missions, next_mission['Mission ID'])) + ' - ' + str(next_mission['Mission ID']))

        # If adding all flights in this mission would exceed max_flights, skip to next mission
        if current_flights + count_flights_in_mission(missions, next_mission['Mission ID']) > max_flights or hoursWorked + ((get_mission_distance(missions, next_mission['Mission ID']) / knots) + (count_flights_in_mission(missions, next_mission['Mission ID']) * 0.6)) > max_Hours:
            missions = missions[missions['Mission ID'] != next_mission['Mission ID']]
            print('Too many flights to fit')
            continue
        else:
            current_flights += count_flights_in_mission(missions, next_mission['Mission ID'])
            print('Adding flights - current flights now: ' + str(current_flights))
            
            # Add the hours for the mission
            hoursWorked += (get_mission_distance(missions, next_mission['Mission ID']) / knots) + (count_flights_in_mission(missions, next_mission['Mission ID']) * 0.6)
            print('Added hours - total now: ' + str(hoursWorked))
            
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
    missions = pd.read_csv('flights.csv')
    fbos = pd.read_csv('FBOs.csv')

    missions = missions.merge(fbos, left_on='FBOId', right_on='ID', how='left')
    missions = missions.drop(columns=['FBOId', 'ID', 'Airport Name', 'ICAO'])
    missions = missions.rename(columns={'FBONAME': 'FBOId'})

    missions = filter_human_only(missions, human_only)
    missions = filter_last_minute(missions, last_minute)
    missions = filter_by_expiration(missions, hours)
    missions = filter_pax(missions, minPax0, maxPax0, minPax1, maxPax1, minPax2, maxPax2, minCargo, maxCargo)
    
    if playerMixup != 1:
        missions = missions.sort_values(by='Pay', ascending=False)
    else:
        missions = player_mixup(missions)
        missions = missions.sample(frac=1)
        
    
    global route, work_order, current_flights, hoursWorked, knots, maxHours
    current_flights = 0
    route = pd.DataFrame()
    hoursWorked = 0
    work_order = pd.DataFrame(columns=['Order', 'Mission ID', 'DepartureICAO', 'DestinationICAO', 'Distance', 'Descript'])
    dfs(missions, starting_icao, route_amount, max_Hours)

    if len(route) > 0 and route.iloc[-1]['DestinationICAO'] != starting_icao:
        print('Warning: the final flight does not return to the starting ICAO.')
    elif len(route) < route_amount:
        print('Warning: less than ' + str(route_amount) + ' flights have been selected.')
    else:
        print('A route has been found.')

    jobs_take = pd.DataFrame()
    jobs_take = route.copy()
    jobs_take = jobs_take.groupby('Mission ID').first().reset_index()[['FBOId', 'Pay']]
    total_pay = jobs_take['Pay'].sum()
    jobs_take['Pay'] = jobs_take['Pay'].map('{:,.0f}'.format)
    jobs_take = jobs_take.sort_values(by='FBOId', ascending=True)
    
    
    route.to_csv('output.csv', index=False)
    #workOrderName = input('Please type the aircraft name: ').upper()

    work_order.to_csv('workorder_' + workOrderName + '.csv', index=False)
    jobs_take.to_csv('JobsToTake.csv', index=False, mode='a', header=not os.path.exists('JobsToTake.csv'))
    return route, work_order, jobs_take, total_pay, work_order['Mission ID'].tolist()

def automation_flights(starting_icao, aircraftType, preset, aircraftName):

    global minPax0, maxPax0, minPax1 ,maxPax1, minPax2, maxPax2, minCargo, maxCargo, knots, opCost

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

    if aircraftType == 'Boeing 787-10  Mk2':
        minPax0 = 154
        maxPax0 = 222
        minPax1 = 42
        maxPax1 = 62
        minPax2 = 21
        maxPax2 = 31
        minCargo = 20000
        maxCargo = 30000
        knots = 488
        opCost = 236034

    last_minute = 1 #disables last minute running
    playerMixup = 0

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

    route, work_order, jobs_take, total_pay, selected_mission_ids = plan_route(starting_icao, 1, last_minute, hours, route_amount, max_Hours, playerMixup, aircraftName)

    if selected_mission_ids:
        remove_selected_missions(selected_mission_ids)

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


#Running the new queries
deleteJobsToTake = input('Do you want to delete the jobsToTake file? Type 1 if yes: ')

if deleteJobsToTake == "1":
    os.remove('JobsToTake.csv')

    file_list = os.listdir()
    for file_name in file_list:
        if 'workorder_' in file_name:
            os.remove(file_name)

RunNewQueries = input("Do you want to rerun the query import? Type 1 if yes: ")

if RunNewQueries == "1":
    command = ["python", "1. ImportNewFlights.py"]
    # Run the command and wait for it to finish
    process = subprocess.Popen(command)
    process.wait()

    # Check the return code of the subprocess
    return_code = process.returncode
    if return_code == 0:
        print("The other script executed successfully.")
    else:
        print("Failed")
    #End running queries

aircraftInOperation = pd.read_csv('AircraftInOperation.csv')
aircraft_List = aircraftInOperation['Aircraft'].tolist()
aircraft_List = get_workorders(aircraft_List)

for aircraft_info in aircraft_List:
    hours_before_inspection = aircraft_info['HoursBefore100HInspection']
    if hours_before_inspection != 'N/A':  # Ensure the data exists
        hours_before_inspection = float(hours_before_inspection)  # Convert to float if necessary
        if 52 <= hours_before_inspection:
            preset = "d"
        elif 39 <= hours_before_inspection < 52:
            preset = "c"
        elif 26 <= hours_before_inspection < 39:
            preset = "b"
        
        if hours_before_inspection >= 26:  # Aircraft doesn't need maintenance
            automation_flights(aircraft_info['Airport'], aircraft_info['DisplayName'], preset, aircraft_info['Aircraft'])
