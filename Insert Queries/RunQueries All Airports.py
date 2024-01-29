import pyautogui
import pyperclip
import pandas as pd
import shutil
import csv
import sys
import time
import os
import subprocess
import random
import datetime

def myexcepthook(type, value, traceback, oldhook=sys.excepthook):
    oldhook(type, value, traceback)
    aaaaaaaa = input("")

sys.excepthook = myexcepthook

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


def checkFiles(selected_airport, aircraft):
    # Returns true if the airport needs to be updated

    newFile = []
    with open(aircraft + '.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) # skip header
        newFile = list(reader)

    oldFlights = []
    with open('.\ChangeCheck\LastFlightData.csv', 'r') as oldFlightsFile:
        reader = csv.reader(oldFlightsFile)
        next(reader) # skip header
        oldFlights = list(reader)

    for new_line in newFile:
        if new_line[0] == selected_airport:
            airport_count = 0
            for old_line in oldFlights:
                if new_line[0] == old_line[0] and new_line[1] == old_line[1] and old_line[3] == aircraft + '.csv':
                    if new_line[2] != old_line[2]:
                        #Something that doesn't match is found
                        return True
                    if new_line[1] == old_line[1]:
                        #Found a match
                        airport_count += 1

            if airport_count == 0 and new_line[2] == 'True':
                #Airport not found and is marked as true
                #print_with_timestamp('AIRPORT COUNT CHECK FAIL: Checking: ' + new_line[0] + 'Dest airport: ' + new_line[1] + ' Airport count: ' + str(airport_count))
                return True
            #print_with_timestamp('Checking: ' + new_line[0] + 'Dest airport: ' + new_line[1] + ' Airport count: ' + str(airport_count))
    
    return False


def update_airport(selected_airport):
    # We are going to check if the airport needs updating or not, this will return true if it needs updating
   
    # Put all aircraft type in here:
    if any(checkFiles(selected_airport, aircraft) for aircraft in ['A320', 'TBM9', 'B78X', 'B78X1', 'B78X2', 'B78X3']):
        return True

    with open('Onair Dispatch Helper - QueryMap.csv', 'r') as file:
        next(file) # Skipping header
        queries = file.readlines()
        
    with open('.\ChangeCheck\QueryMap.csv', 'r') as oldFile:
        next(oldFile) # Skipping header
        oldQueries = oldFile.readlines()
    
    for line in queries:
        queryfields = line.strip().split(',')
        query_airport = queryfields[0]
        
        if query_airport == selected_airport:
            for old_line in oldQueries:
                old_query_fields = old_line.strip().split(',')
                old_query_airport = old_query_fields[0]
                
                if old_query_airport == query_airport:
                    if old_query_fields[1:] != queryfields[1:]: # Simplify comparison by checking the entire lists
                        return True
                    break  # If match is found, break out of the loop
            else:  # If loop was not broken (no match was found), return True
                return True

    return False


input("This is the 4k screen version, with the program maximised. This is the ALL AIRPORTS VERSION, IT TAKES A FUCKING WHILE. MAKE SURE YOU'RE ON THE MY FBO'S SCREEN ON PAGE 1. Check this and then hit Enter..")
#new_queries = int(input("Type 1 if this is the first time the queries are being setup to enter return legs, else type 0 : "))

#Import raw flight data and output processed table
df = pd.read_csv("Onair Dispatch Helper - A320 ROUTES.csv")
df.rename(columns={df.columns[0]: 'Origin'}, inplace=True)
melted_df = df.melt(id_vars=df.columns[0], var_name='Destination', value_name='Approved')
#Sort to match Onair
sorted_df = melted_df.sort_values(by=['Destination', 'Origin'])
sorted_df.to_csv('A320.csv', index=False)

df = pd.read_csv("Onair Dispatch Helper - 787 ROUTES.csv")
df.rename(columns={df.columns[0]: 'Origin'}, inplace=True)
melted_df = df.melt(id_vars=df.columns[0], var_name='Destination', value_name='Approved')
#Sort to match Onair
sorted_df = melted_df.sort_values(by=['Destination', 'Origin'])
sorted_df.to_csv('B78X3.csv', index=False)

df = pd.read_csv("Onair Dispatch Helper - 787 ROUTES.csv")
df.rename(columns={df.columns[0]: 'Origin'}, inplace=True)
melted_df = df.melt(id_vars=df.columns[0], var_name='Destination', value_name='Approved')
#Sort to match Onair
sorted_df = melted_df.sort_values(by=['Destination', 'Origin'])
sorted_df.to_csv('B78X1.csv', index=False)

df = pd.read_csv("Onair Dispatch Helper - 787 ROUTES.csv")
df.rename(columns={df.columns[0]: 'Origin'}, inplace=True)
melted_df = df.melt(id_vars=df.columns[0], var_name='Destination', value_name='Approved')
#Sort to match Onair
sorted_df = melted_df.sort_values(by=['Destination', 'Origin'])
sorted_df.to_csv('B78X2.csv', index=False)

df = pd.read_csv("Onair Dispatch Helper - 787 ROUTES.csv")
df.rename(columns={df.columns[0]: 'Origin'}, inplace=True)
melted_df = df.melt(id_vars=df.columns[0], var_name='Destination', value_name='Approved')
#Sort to match Onair
sorted_df = melted_df.sort_values(by=['Destination', 'Origin'])
sorted_df.to_csv('B78X.csv', index=False)

df = pd.read_csv("Onair Dispatch Helper - TBM ROUTES.csv")
df.rename(columns={df.columns[0]: 'Origin'}, inplace=True)
melted_df = df.melt(id_vars=df.columns[0], var_name='Destination', value_name='Approved')
#Sort to match Onair
sorted_df = melted_df.sort_values(by=['Destination', 'Origin'])
sorted_df.to_csv('TBM9.csv', index=False)


df = pd.read_csv("Onair Dispatch Helper - CJ4 ROUTES.csv")
df.rename(columns={df.columns[0]: 'Origin'}, inplace=True)
melted_df = df.melt(id_vars=df.columns[0], var_name='Destination', value_name='Approved')
#Sort to match Onair
sorted_df = melted_df.sort_values(by=['Destination', 'Origin'])
sorted_df.to_csv('CJ4.csv', index=False)

#Starting at the first airport
fbo_offset = 320
pyautogui.click(x=31, y=226)
pyautogui.sleep(0.1)

with open('Onair Dispatch Helper - FBOs.csv', 'r') as file:
    next(file) #skip header
    fbos = file.readlines()
    
for line in fbos:
    if fbo_offset >= 1080:
        fbo_offset = 320 #We must have hit the bottom of the page. 
        pyautogui.click(x=101, y=230) #Click next page
        pyautogui.sleep(1) #wait for the cunt to load

    #We are going to put the code in here to check if the airport needs updating
    
    
    #Click the FBO line
    pyautogui.click(x=1000, y=fbo_offset)
    pyautogui.sleep(0.1)
    #Copy the data
    pyautogui.hotkey('ctrl', 'c')
    pyautogui.sleep(1.5)
    #Grab the 7th field
    
    FBO_Menu_Selected = pyperclip.paste().split("\t")
    
    #Check if the airport needs updating
    if update_airport(FBO_Menu_Selected[6]) == False:
        fbo_offset += 36
        continue
    

    pyautogui.click(x=145, y=fbo_offset)
    pyautogui.sleep(10) #We will wait 10 seconds for the FBO page to load. Fuck onair is slow
    fbo_offset += 36 #Add 36 to get to the next one

    
    
    # Finding out the FBO Name, putting on the clipboard and then assigning this to selected_airport
    pyautogui.click(x=250, y=266)
    pyautogui.sleep(0.2)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1.5)

    selected_airport = pyperclip.paste()

    #Setting the query pixels and the number
    queryvalue = 1900
    query_number = 1




    with open('Onair Dispatch Helper - QueryMap.csv', 'r') as file:
        next(file)
        queries = file.readlines()
        #Skipping header

    for line in queries:
        queryfields = line.strip().split(',')
        query_airport = queryfields[0]

    # for line in queries:
        # queryfields = line.strip().split('\t')

        # # Extracting the queries
        # #Class info:
        # #0 - None, 1 - Eco, 2 - Business, 3 - First
        # query_name = queryfields[0]
        # query_true = int(queryfields[1])
        # query_pax = queryfields[2]
        # query_class = int(queryfields[3])

        #if the airport matches
        if query_airport == selected_airport:

            while query_number <= 10: # Selecting the 10 fields
            
                # Select Query
                pyautogui.click(x=queryvalue, y=800)
                pyautogui.sleep(0.2)
                
                if queryfields[query_number] != "N/A":

                    if queryfields[query_number] == "A320":
                        query_pax = '155'
                        query_class = 1 #0 - None, 1 - Eco, 2 - Business, 3 - First
                        cargo_min = '0'
                    
                    if queryfields[query_number] == "TBM9":
                        query_pax = '3'
                        query_class = 3 #0 - None, 1 - Eco, 2 - Business, 3 - First
                        cargo_min = '0'
                        
                        
                    if queryfields[query_number] == "B78X":
                        query_pax = '262'
                        query_class = 3 #0 - None, 1 - Eco, 2 - Business, 3 - First
                        cargo_min = '27500'

                    if queryfields[query_number] == "B78X1":
                        query_pax = '262'
                        query_class = 3 #0 - None, 1 - Eco, 2 - Business, 3 - First
                        cargo_min = '24000'                        
 

                    if queryfields[query_number] == "B78X2":
                        query_pax = '262'
                        query_class = 3 #0 - None, 1 - Eco, 2 - Business, 3 - First
                        cargo_min = '20000' 
                        
                        
                    if queryfields[query_number] == "B78X3":
                        query_pax = '262'
                        query_class = 3 #0 - None, 1 - Eco, 2 - Business, 3 - First
                        cargo_min = '0' 
                    
                    if queryfields[query_number] == "CJ4":
                        query_pax = '7'
                        query_class = 3 #0 - None, 1 - Eco, 2 - Business, 3 - First
                        cargo_min = '0' 

                    #Remove old pax
                    pyautogui.click(x=2684, y=942)
                    pyautogui.sleep(0.1)
                    pyautogui.write("0")
                    
                    #Remove old cargo
                    pyautogui.click(x=2684, y=890)
                    pyautogui.sleep(0.1)
                    pyautogui.write("0")
                    
                    #Add pax count
                    pyautogui.click(x=2600, y=942)
                    pyautogui.sleep(0.1)
                    pyautogui.write(query_pax)
                    
                    #Add Cargo
                    pyautogui.click(x=2600, y=890)
                    pyautogui.sleep(0.1)
                    pyautogui.write(cargo_min)

                    #preferred seats
                    pyautogui.click(x=2590, y=980)
                    pyautogui.sleep(0.5)
                    
                    #Select based on class
                    pyautogui.click(x=2590, y=1010 + (33 * query_class)) 
                    pyautogui.sleep(0.1)
                    
                    
                    new_queries = 0
                    # Capture a region (top-left x, top-left y, width, height)
                    screenshot = pyautogui.screenshot(region=(2386,1022,4,4))

                    # Iterate over the image pixels
                    for y in range(screenshot.height):
                        for x in range(screenshot.width):
                            # If the pixel matches the RGB values, print a message
                            if screenshot.getpixel((x, y)) == (154, 164, 176):
                                new_queries = 1               
                    
                    #If we need to add return legs, add them now:
                    if new_queries == 0:
                        pyautogui.click(x=2390, y=1020)
                        pyautogui.sleep(0.5)

                    # Select "Selected FBOs"
                    pyautogui.sleep(1)
                    pyautogui.click(x=2166, y=862)
                    pyautogui.sleep(1)
                    pyautogui.click(x=2166, y=900)
                    pyautogui.sleep(0.5)
                    
                    
                    # Unselect All and then select the first record
                    pyautogui.click(x=2290, y=900)
                    pyautogui.sleep(0.1)
                    pyautogui.click(x=1870, y=942)
                    pyautogui.sleep(0.1)
                    pyautogui.click(x=1870, y=942)
                    pyautogui.sleep(0.1)
                    

                    # Process each line in the input file
                    with open(queryfields[query_number] + '.csv', 'r') as file:
                        lines = file.readlines()

                    for line in lines:
                        # Split the line into fields (assuming comma separated values)
                        fields = line.strip().split(',')

                        # Extract the relevant information
                        origin = fields[0]
                        destination = fields[1]
                        is_true = fields[2]

                        # Check whether the origin is the same as the FBO we are looking for
                        if origin == selected_airport and selected_airport != destination:
                        
                            # Check if the record is true or false
                            if is_true == 'True':
                                # Perform action for true record
                                # Send spacebar key
                                pyautogui.press('space')
                                #print_with_timestamp(f"Sent spacebar for airport: {query_name}")
                                pyautogui.sleep(0.01)
                            
                            # Send down arrow key regardless of the record
                            pyautogui.press('down')
                            #print_with_timestamp(f"Sent down arrow for airport: {query_name}")
                            pyautogui.sleep(0.05)

                # Adding 100 to the query to go to the next one and going to the next query
                print_with_timestamp(f"Completed query:: {query_number} for {selected_airport}")
                queryvalue += 100
                query_number += 1
    #Commit changes
    #Click save query
    pyautogui.click(x=2790, y=745)
    pyautogui.sleep(5)
    #Click back
    pyautogui.click(x=30, y=116)
    pyautogui.sleep(1)
    print_with_timestamp(f"Completed airport ::{selected_airport}")
    


    
    
#Saving all the data

# define the names of the files to read from
filenames = ['A320.csv', 'B78X.csv', 'TBM9.csv', 'B78X1.csv', 'B78X2.csv', 'B78X3.csv']

# define a list to store the dataframes
dfs = []

# read each csv file, add a new column, and add it to the list
for filename in filenames:
    temp_df = pd.read_csv(filename)
    temp_df['source_file'] = filename  # Add a new column with the filename
    dfs.append(temp_df)

# concatenate all the dataframes in the list
df = pd.concat(dfs, ignore_index=True)

# save the result to a new csv
df.to_csv('.\ChangeCheck\LastFlightData.csv', index=False)
#Copy querymap
shutil.copy('Onair Dispatch Helper - QueryMap.csv', '.\ChangeCheck\QueryMap.csv')


print_with_timestamp("All records processed.")

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
# Define the old and new file paths
old_file_path = 'Log.txt'
new_file_name = f"Log_{timestamp}.txt"
new_file_path = os.path.join('logs', new_file_name)

input()
