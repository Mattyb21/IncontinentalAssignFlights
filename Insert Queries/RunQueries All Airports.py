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



def myexcepthook(type, value, traceback, oldhook=sys.excepthook):
    oldhook(type, value, traceback)
    aaaaaaaa = input("")

sys.excepthook = myexcepthook

def print_matched_destinations(airports_table):
    # Iterate through each row in the airports_table
    for index, row in airports_table.iterrows():
        # Check if the Match field is True for the current row
        if row['Match']:
            # Print the airport for which Match is True
            print(f"Match found for airport: {row['Airport']}")
            print_with_timestamp(f"Match found for airport: {row['Airport']}")

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

def get_changed_aircraft(old_df, new_df):
    # Compares two DataFrames to identify aircraft with changes in their definitions.

    # Parameters:
    # old_df (DataFrame): The old DataFrame of aircraft definitions.
    # new_df (DataFrame): The new DataFrame of aircraft definitions.

    # Returns:
    # list: A list of aircraft that have at least one attribute changed.
 
    changed_aircraft = []

    # Iterate through each row in the new DataFrame
    for _, new_row in new_df.iterrows():
        # Find the corresponding row in the old DataFrame based on the 'Aircraft' column
        old_row = old_df[old_df['Aircraft'] == new_row['Aircraft']]
        
        # If there's no matching row, continue to the next row (new aircraft not in old DataFrame)
        if old_row.empty:
            changed_aircraft.append(new_row['AircraftCode'])
            continue
        
        # Compare all columns for changes, excluding the index
        if not old_row.values[0][1:].tolist() == new_row.values[1:].tolist():
            changed_aircraft.append(new_row['AircraftCode'])
    
    return changed_aircraft

def get_changed_airports_with_extract(old_map_df, new_map_df, changed_aircraft_list, old_extract_df, new_extract_df):

    # Identifies airports with changes in their query maps, references to changed aircraft, or changes in extract data.
    # If extract entries have changed, appends "INCOZ - " to the dpt_airport field before adding it to the changed airports list.

    # Parameters:
    # old_map_df (DataFrame): The old DataFrame of airport query maps.
    # new_map_df (DataFrame): The new DataFrame of airport query maps.
    # changed_aircraft_list (list): A list of aircraft codes that have changed.
    # old_extract_df (DataFrame): The old DataFrame of extract data.
    # new_extract_df (DataFrame): The new DataFrame of extract data.

    # Returns:
    # list: A list of airports that have changes or reference a changed aircraft, including modified extract entries.
    
    changed_airports = []

    # Compare query maps and references to changed aircraft
    for _, new_row in new_map_df.iterrows():
        airport_name = new_row['Airport']
        old_row = old_map_df[old_map_df['Airport'] == airport_name]

        has_changed = False
        if old_row.empty or not old_row.values[0][1:].tolist() == new_row.values[1:].tolist():
            has_changed = True
        else:
            for aircraft_code in changed_aircraft_list:
                if aircraft_code in new_row.values.tolist():
                    has_changed = True
                    break

        if has_changed and airport_name not in changed_airports:
            changed_airports.append(airport_name)

    # Create sets of unique identifiers for each DataFrame to compare combinations
    old_combinations = set(old_extract_df.apply(lambda row: (row['dpt_airport'], row['arr_airport'], row['OnAirAircraftType']), axis=1))
    new_combinations = set(new_extract_df.apply(lambda row: (row['dpt_airport'], row['arr_airport'], row['OnAirAircraftType']), axis=1))

    # Identify new combinations or those that have been removed
    added_combinations = new_combinations - old_combinations
    removed_combinations = old_combinations - new_combinations

    # Process added and removed combinations
    for dpt_airport, _, _ in added_combinations.union(removed_combinations):
        modified_airport = "INCOZ - " + dpt_airport
        if modified_airport not in changed_airports:
            changed_airports.append(modified_airport)

    return changed_airports

def get_aircraft_details(query_definitions_df, aircraft_code):
    # Find the row with the matching AircraftCode
    matching_row = query_definitions_df[query_definitions_df['AircraftCode'] == aircraft_code]
    
    # Check if a matching row was found
    if not matching_row.empty:
        # Return the first matching row as a dictionary (assuming AircraftCode is unique)
        return matching_row.iloc[0].to_dict()
    else:
        # Return None or an empty dictionary if no match was found
        print_with_timestamp("There was an error finding the aircraft in the definitions: " + aircraft_code)
        input("There was an error finding the aircraft in the definitions: " + aircraft_code)

def find_arrival_locations(airport, OnAirAircraftType, query_extract_df, query_map_df):
    # Step 1: Create a new table with all airports from query_map_df and a True/False column
    airports_table = pd.DataFrame(query_map_df['Airport'].unique(), columns=['Airport'])
    airports_table['Match'] = False  # Initialize all values to False

    # Step 2: Check for matches and update the table
    for index, row in query_extract_df.iterrows():
        if row['dpt_airport'] == airport and row['OnAirAircraftType'] == OnAirAircraftType:
            # Find matching arr_airport in the airports_table and set Match to True
            arr_airport_index = airports_table[airports_table['Airport'] == row['arr_airport']].index
            if not arr_airport_index.empty:
                airports_table.at[arr_airport_index[0], 'Match'] = True

    return airports_table

def assign_destinations(airports_table, airport):
    # Iterate through each row in the airports_table
    for index, row in airports_table.iterrows():
        # Check if the Match field is True for the current row
        if row['Match']:
            pyautogui.press('space')
            time.sleep(0.25)

        
        if airport != row['Airport']:
            pyautogui.press('down')
            time.sleep(0.05)

def airport_updater(airport, query_map_df, query_definitions_df, query_extract_df):
    #Setting the pixel to start on
    queryvalue = 1900
    #Setting first query
    query_number = 1
    #Getting the row from query map which we will use
    row = query_map_df[query_map_df['Airport'] == airport]
    
    #Checking we have actually got the right airport in front of us
    time.sleep(10)
    pyautogui.click(x=250, y=266)
    pyautogui.sleep(0.2)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1.5)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1.5)
    
    selected_airport = pyperclip.paste()
    
    if selected_airport != airport:
        #something has gone wrong, we've got the wrong airport up.
        print_with_timestamp("Something is wrong, wrong airport selected. Expecting: " + airport)
        input("Something is wrong, wrong airport selected. Expecting: " + airport)

    #Select the query
    for query_number in range(1, 11):  # Columns named 1 to 10
            if not row.empty and str(query_number) in row.columns:
                query_code = row.iloc[0][str(query_number)]
                aircraft_details = get_aircraft_details(query_definitions_df, query_code)
                
                # Process based on the query_code value
                # Example process: Print the query_code. Replace this with your actual process
                print_with_timestamp(f"Processing {airport}, Query {query_number}: {query_code}")
                
                #Select query
                pyautogui.click(x=queryvalue, y=1253)
                pyautogui.sleep(0.2)
                
                #Remove old pax - select max pax
                pyautogui.click(x=2731, y=1384)
                pyautogui.sleep(0.1)
                pyautogui.write("0")
                
                #Remove old cargo - select max cargo
                pyautogui.click(x=2748, y=1333)
                pyautogui.sleep(0.1)
                pyautogui.write("0")
                
                #Add pax count
                pyautogui.click(x=2601, y=1379)
                pyautogui.sleep(0.1)
                pyautogui.write(str(aircraft_details['Pax min']))
                
                #Add Cargo
                pyautogui.click(x=2627, y=1341)
                pyautogui.sleep(0.1)
                pyautogui.write(str(aircraft_details['Cargo min']))
                
                #preferred seats
                pyautogui.click(x=2614, y=1434)
                pyautogui.sleep(0.5)
                
                #Select based on class
                pyautogui.click(x=2590, y=1462 + (33 * int(aircraft_details['Class'])))
                pyautogui.sleep(0.1)
                
                new_queries = 0
                # Capture a region (top-left x, top-left y, width, height)
                screenshot = pyautogui.screenshot(region=(2386,1472,4,4))

                # Iterate over the image pixels
                for y in range(screenshot.height):
                    for x in range(screenshot.width):
                        # If the pixel matches the RGB values, print a message
                        if screenshot.getpixel((x, y)) == (154, 164, 176):
                            new_queries = 1
                #If we need to add return legs, add them now:
                if new_queries == 0:
                    pyautogui.click(x=2387, y=1469)
                    pyautogui.sleep(0.5)

                # Select "Selected FBOs"
                pyautogui.sleep(1)
                pyautogui.click(x=2130, y=1309)
                pyautogui.sleep(1)
                pyautogui.click(x=2132, y=1344)
                pyautogui.sleep(0.5)
                
                
                # Unselect All and then select the first record
                pyautogui.click(x=2273, y=1354)
                pyautogui.sleep(0.1)
                pyautogui.click(x=1866, y=1393)
                pyautogui.sleep(0.1)
                pyautogui.click(x=1866, y=1393)
                pyautogui.sleep(0.1)
                
                #This will make a table in alphabetical order 
                arrival_locations = find_arrival_locations(airport, query_code, query_extract_df, query_map_df)
                assign_destinations(arrival_locations, airport)
                
                queryvalue += 100
                
    
    #Click save query
    pyautogui.click(x=2790, y=745)
    pyautogui.sleep(5)
    #Click back
    pyautogui.click(x=30, y=116)
    pyautogui.sleep(3)

input("Please ensure OnAir is open behind this window, press enter when ready...")
pyautogui.click(x=913, y=0)
time.sleep(1)

# Load the CSV files into DataFrame objects
query_map_df = pd.read_csv('Onair Dispatch Helper - QueryMap.csv')
query_definitions_df = pd.read_csv('Onair Dispatch Helper - QueryDefinitions.csv')
query_extract_df = pd.read_csv('Onair Dispatch Helper - QueryExtract.csv')

old_query_map_df = pd.read_csv('ChangeCheck\Onair Dispatch Helper - QueryMap.csv')
old_query_definitions_df = pd.read_csv('ChangeCheck\Onair Dispatch Helper - QueryDefinitions.csv')
old_query_extract_df = pd.read_csv('ChangeCheck\Onair Dispatch Helper - QueryExtract.csv')


changed_aircraft = get_changed_aircraft(old_query_definitions_df, query_definitions_df) #If aircraft definition has changed
changed_airports = get_changed_airports_with_extract(old_query_map_df, query_map_df, changed_aircraft, old_query_extract_df, query_extract_df) #If airport has been changed (including aircraft associated with airport)

print_with_timestamp("Changed aircraft:")
print_with_timestamp(changed_aircraft)
print_with_timestamp("Changed airports:")
print_with_timestamp(changed_airports)
print_with_timestamp('Expected ETA: ' + str((len(changed_airports) * 6)) + ' minutes')

if not changed_airports:
    print_with_timestamp("No changed airports detected.")
else:
    #Fixing up query extract with the prefix to match FBO name
    query_extract_df['dpt_airport'] = "INCOZ - " + query_extract_df['dpt_airport']
    query_extract_df['arr_airport'] = "INCOZ - " + query_extract_df['arr_airport']

    #Open the FBO page
    #Click My Virtual Airline
    pyautogui.click(x=114, y=78)
    time.sleep(1)
    #Click My FBOs
    pyautogui.click(x=137, y=470)
    time.sleep(12)

    #click the first line of FBO - services column
    pyautogui.click(x=340, y=291)
    time.sleep(1)

    number_of_fbos = len(query_map_df)

    for i in range(number_of_fbos):
        #Copy the line
        pyautogui.hotkey('ctrl', 'c')
        pyautogui.sleep(1.5)
        pyautogui.hotkey('ctrl', 'c')
        pyautogui.sleep(1.5)
        
        #Take the clipboard data
        FBO_Menu_Selected = pyperclip.paste().split("\t")
        
        if FBO_Menu_Selected[6] in changed_airports:
            #Needs updating
            print('Updating ' + FBO_Menu_Selected[6])
            pyautogui.press('left')
            pyautogui.sleep(1)
            pyautogui.press('tab')
            pyautogui.sleep(1)
            pyautogui.press('enter')
            pyautogui.sleep(10) #Waiting for FBO page to load
            airport_updater(FBO_Menu_Selected[6], query_map_df, query_definitions_df, query_extract_df)
            print_with_timestamp("Completed airport: " + FBO_Menu_Selected[6])
            
            #Getting back to where we started in the column
            pyautogui.press('down')
            pyautogui.sleep(1)
            pyautogui.press('right')
            pyautogui.sleep(1)
        
        #Next FBO in the list
        pyautogui.press('down')
        pyautogui.sleep(1)



    #Copying the files to changecheck
    # Define the source files
    print_with_timestamp("Copying files to ChangeCheck")
    files_to_copy = [
        "Onair Dispatch Helper - QueryExtract.csv",
        "Onair Dispatch Helper - QueryDefinitions.csv",
        "Onair Dispatch Helper - QueryMap.csv"
    ]

    # Define the target folder name
    target_folder_name = "ChangeCheck"

    # Construct the path to the target folder assuming it's in the same location as the script
    target_folder_path = os.path.join(os.getcwd(), target_folder_name)

    # Ensure the target folder exists, create if it doesn't
    os.makedirs(target_folder_path, exist_ok=True)

    # Copy each file to the target folder
    for file_name in files_to_copy:
        source_file_path = os.path.join(os.getcwd(), file_name)  # Assuming files are in the same directory as the script
        target_file_path = os.path.join(target_folder_path, file_name)
    
        # Copy the file
        shutil.copy(source_file_path, target_file_path)
        print(f"Copied {file_name} to {target_folder_path}")

print_with_timestamp("All airports refreshed")
input("Done")
