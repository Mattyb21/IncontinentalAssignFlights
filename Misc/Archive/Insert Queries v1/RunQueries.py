import pyautogui
import pyperclip
from screeninfo import get_monitors
import pandas as pd

input("This is the 4k screen version, with the program maximised. Check this and then hit Enter..")
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
sorted_df.to_csv('B787.csv', index=False)

df = pd.read_csv("Onair Dispatch Helper - TBM ROUTES.csv")
df.rename(columns={df.columns[0]: 'Origin'}, inplace=True)
melted_df = df.melt(id_vars=df.columns[0], var_name='Destination', value_name='Approved')
#Sort to match Onair
sorted_df = melted_df.sort_values(by=['Destination', 'Origin'])
sorted_df.to_csv('TBM9.csv', index=False)



# Finding out the FBO Name, putting on the clipboard and then assigning this to selected_airport
pyautogui.click(x=250, y=266)
pyautogui.sleep(0.2)
pyautogui.hotkey('ctrl', 'a')
pyautogui.hotkey('ctrl', 'c')

#
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
                
                if queryfields[query_number] == "TBM9":
                    query_pax = '3'
                    query_class = 3 #0 - None, 1 - Eco, 2 - Business, 3 - First
                    
                    
                if queryfields[query_number] == "B787":
                    query_pax = '300'
                    query_class = 0 #0 - None, 1 - Eco, 2 - Business, 3 - First
                

                #Remove old pax
                pyautogui.click(x=2684, y=942)
                pyautogui.sleep(0.1)
                pyautogui.write("0")
                
                #Add pax count
                pyautogui.click(x=2600, y=942)
                pyautogui.sleep(0.1)
                pyautogui.write(query_pax)

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
                pyautogui.click(x=2166, y=862)
                pyautogui.sleep(0.3)
                pyautogui.click(x=2166, y=900)
                pyautogui.sleep(0.1)
                
                
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
                            #print(f"Sent spacebar for airport: {query_name}")
                            pyautogui.sleep(0.01)
                        
                        # Send down arrow key regardless of the record
                        pyautogui.press('down')
                        #print(f"Sent down arrow for airport: {query_name}")
                        pyautogui.sleep(0.05)

            # Adding 100 to the query to go to the next one and going to the next query
            print(f"Completed query:: {query_number} for {selected_airport}")
            queryvalue += 100
            query_number += 1
            

print("All records processed.")
