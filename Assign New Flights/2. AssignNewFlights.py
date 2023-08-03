import pandas as pd
import datetime
import random
import subprocess
import os

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


# def filter_pax(missions, minPax0, maxPax0, minPax1, maxPax1, minPax2, maxPax2, minCargo, maxCargo):
    # # Filter out missions if any flight has 'pax' or 'cargo' lower than the respective min value or higher than the respective max value
    # missions = missions.groupby('Mission ID').filter(
        # lambda x: (x['PaxClass0'].min() >= minPax0 and x['PaxClass0'].max() <= maxPax0) and
                  # (x['PaxClass1'].min() >= minPax1 and x['PaxClass1'].max() <= maxPax1) and
                  # (x['PaxClass2'].min() >= minPax2 and x['PaxClass2'].max() <= maxPax2) and
                  # (x['Cargo'].min() >= minCargo and x['Cargo'].max() <= maxCargo)
    # )
    # return missions
    
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


        # Select the first available flight
        #next_flight = available_flights.iloc[0]

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

    #print('All flights in the mission are:')
    #print(mission_flights[['Mission ID', 'DepartureICAO', 'DestinationICAO']])
    #print('---')

    
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


def plan_route(starting_icao, human_only, last_minute, hours, route_amount, max_Hours, playerMixup):
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
    print(route)
    jobs_take = route.copy()
    print(jobs_take)
    jobs_take = jobs_take.groupby('Mission ID').first().reset_index()[['FBOId', 'Pay']]
    total_pay = jobs_take['Pay'].sum()
    jobs_take['Pay'] = jobs_take['Pay'].map('{:,.0f}'.format)
    jobs_take = jobs_take.sort_values(by='FBOId', ascending=True)
    
    
    route.to_csv('output.csv', index=False)
    workOrderName = input('Please type the aircraft name: ').upper()
    work_order.to_csv('workorder_' + workOrderName + '.csv', index=False)
    jobs_take.to_csv('JobsToTake.csv', index=False, mode='a', header=not os.path.exists('JobsToTake.csv'))
    return route, work_order, jobs_take, total_pay, work_order['Mission ID'].tolist()



starting_icao = input('Enter the Starting ICAO: ').upper()
human_only = int(input('Enter 1 if all flights are to be completed by AI, otherwise enter 0: '))

#if human_only == 0:
    #human_only_amount = int(input('How many human only jobs should we select? Enter #: '))
    
aircraftType = input('Please enter the type of aircraft, i.e. A320, TBM9, B78X: ').upper()

if aircraftType == 'A320':
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
    
if aircraftType == 'TBM9':
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
    
if aircraftType == 'B78X':
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
    
print("Preset info:")
print("EXPIRY | MAINT | # FLIGHT | TYPE")
print("  22   |  13   |    4     |   A ")
print("  44   |  26   |    8     |   B ")
print("  66   |  39   |    12    |   C ")
print("  88   |  52   |    16    |   D ")
print("  110  |  66   |    20    |   E ")
print("  132  |  79   |    24    |   F ")
print("  154  |  92   |    28    |   G ")
print("")

preset = input("If you want to use a preset, please enter it now. Else hit enter: ").lower()
last_minute = 1
playerMixup = 0

if preset == "":
    #last_minute = int(input('Enter 1 to disable all Last Minute flights, otherwise enter 0: '))
    route_amount = int(input('Enter the amount of flights to select, e.g. 20: '))
    hours = int(input('Enter the number of hours for the expiration filter, e.g. 96 for 4 days, 120 for 5: '))
    max_Hours = int(input('Enter the maximum hours before the next required maintenance: '))
    playerMixup = int(input('Enter 1 if you want to enable player mixup, else 0: '))

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
    max_Hours = 92

checkForNewQueries = int(input('Do you want to check for new queries before running? Type 1 for yes: '))

if checkForNewQueries == 1:
    # Specify the command to execute the other Python script
    command = ["python", "1. ImportNewFlights.py"]

    # Run the command and wait for it to finish
    process = subprocess.Popen(command)
    process.wait()

    # Check the return code of the subprocess
    return_code = process.returncode
    if return_code == 0:
        print("The other script executed successfully.")
    else:
        print("The other script encountered an error. Return code:", return_code)



route, work_order, jobs_take, total_pay, selected_mission_ids = plan_route(starting_icao, human_only, last_minute, hours, route_amount, max_Hours, playerMixup)

if selected_mission_ids:
    remove_selected_missions(selected_mission_ids)


print(route)
print(work_order)
print(jobs_take)
total_payStr = str('{:,}'.format(round(total_pay)))
totalProfit = total_pay - (hoursWorked * opCost)
totalProfitStr = str('{:,}'.format(round(totalProfit)))
print('Total pay for package: $' + total_payStr)
print('Total expetected profit: $' + totalProfitStr)
print('Hours worked: ' + str(hoursWorked))
input("Press Enter to exit...")
