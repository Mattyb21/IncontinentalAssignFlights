import pyautogui
import pyperclip
from screeninfo import get_monitors
monitors = get_monitors()

# Select the desired monitor (replace the index with the appropriate value)
monitor_index = 0  # Change this to the index of the desired monitor

aircraft = input('Please enter the aircraft type, current supported= A320, TBM9, B78X: ').upper()
workOrderName = input('Enter work order name (aircraft): ').upper()
load_fuel = int(input('Would you like to automatically load fuel? 1 for YES, 0 for no: '))
rest_crew = int(input('Would you like to automatically rest the crew? 1 for YES, 0 for no: '))

# Ensure that the screen is ready
screen_ready = input('Ensure that you are on the workorder screen and that the correct aircraft has been selected in the top left as well as the correct pilot / copilot and attendants. If this is correct hit enter')

pyautogui.doubleClick(x=200, y=282)
pyautogui.sleep(0.5)
pyautogui.hotkey('ctrl', 'c')

if pyperclip.paste() != 'Work ':
    print('Workorder not correctly set')
    exit()

#Starting the crew off with 0 hours
hoursWorked = 0

pyautogui.hotkey('ctrl', 'a')
pyautogui.write(workOrderName)

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
        
        #Enter the dest icao
        pyautogui.click(x=736, y=474)
        pyautogui.sleep(0.2)
        pyautogui.write(destination)
        
        #Starting line for first payload. We add 33 for each payload we go down        

        pyautogui.click(x=978, y=875)
        pyautogui.sleep(0.2)
        
        pyautogui.hotkey('ctrl', 'c')
        pyautogui.sleep(0.2)
        
        currentPayload = pyperclip.paste().split("\t")
        pyautogui.sleep(0.2)
        
        #Tab across to the load box
        pyautogui.press('tab')
        pyautogui.sleep(0.05)
        pyautogui.press('tab')
        pyautogui.sleep(0.05)
        pyautogui.press('tab')
        pyautogui.sleep(0.05)
        pyautogui.press('tab')
        pyautogui.sleep(0.05)
        pyautogui.press('tab')
        pyautogui.sleep(0.05)
        pyautogui.press('tab')
        pyautogui.sleep(0.05)
        
        fuckedLoop = 0
        #Setting to check we look at the type before we load
        ecoPaxLoaded = 0
        busPaxLoaded = 0
        firstPaxLoaded = 0
        cargoLoaded = 0

        #print("Looking for " + destination + ', currently seeing ' + currentPayload[1])
        
        #Check destination of current payload, that the Legs field is blank, the next field (maybe other work order, test this pls matt you fucking retard) and VA is blank
        
        # YSSY	WSSS	YSSY	#1 Business Passenger Transport - return	51	51	7/1/2023 6:37:00 AM		False	True	False		False	ONES
        #YSSY	YBHM	YSSY	#3 Eco Passenger Transport - return	169	169	6/28/2023 4:22:46 PM		False	True	False		True	
        
        

        
        while fuckedLoop < 100:
            #print("-")
            #print(currentPayload[1] + " - " + str(len(currentPayload[11])) + " - " + currentPayload[12] + " - " + str(len(currentPayload[13])) + " - " + currentPayload[3][:2] + currentPayload[3][-1:] + " - " + currentPayload[3][:2] + " - " + currentPayload[3][-1:])
            
            #Check to see if the current record matches
            if currentPayload[1] == destination and len(currentPayload[11]) == 0 and currentPayload[12] != 'True' and len(currentPayload[13]) < 4 and descript == currentPayload[3][:2] + currentPayload[3][-1:] or currentPayload[1] == destination and len(currentPayload[11]) == 0 and currentPayload[12] != 'True' and len(currentPayload[13]) < 4 and descript == currentPayload[3][:2] and currentPayload[3][-1:] != "n":
                #Load the job
                if "Eco" in currentPayload[3] and ecoPaxLoaded == 0:
                    pyautogui.press('tab')
                    pyautogui.sleep(0.05)
                    pyautogui.press('space')
                    pyautogui.sleep(0.05)
                    ecoPaxLoaded = 1

                if "Bus" in currentPayload[3] and busPaxLoaded == 0:
                    pyautogui.press('tab')
                    pyautogui.sleep(0.05)
                    pyautogui.press('space')
                    pyautogui.sleep(0.05)
                    busPaxLoaded = 1
                
                if "First" in currentPayload[3] and firstPaxLoaded == 0:
                    pyautogui.press('tab')
                    pyautogui.sleep(0.05)
                    pyautogui.press('space')
                    pyautogui.sleep(0.05)
                    firstPaxLoaded = 1
                    
                if "Cargo" in currentPayload[3] and cargoLoaded == 0:
                    pyautogui.press('tab')
                    pyautogui.sleep(0.05)
                    pyautogui.press('space')
                    pyautogui.sleep(0.05)
                    cargoLoaded = 1


            #currentPayload[1] != destination or len(currentPayload[11]) > 0 or currentPayload[12] != 'False' or len(currentPayload[13]) > 2:
            pyautogui.press('down')
            pyautogui.sleep(0.4)
            
            #Copy Next Row
            pyautogui.hotkey('ctrl', 'c')
            pyautogui.sleep(0.1)

            if pyperclip.paste().split("\t") == currentPayload:
                #There's probably no more jobs, time to move to the next job
                break

            currentPayload = pyperclip.paste().split("\t")
            fuckedLoop += 1
            if fuckedLoop == 100:
                print('Probably no job available that matches the destination airport')
                exit()           

        #We should have loaded all the jobs now
        fuckedLoop = 0        
        ecoPaxLoaded = 0
        busPaxLoaded = 0
        firstPaxLoaded = 0
        cargoLoaded = 0
        if aircraft == 'A320':
            ffph = 847
            knots = 447
            
        if aircraft == 'TBM9':
            ffph = 54
            knots = 330
            
        if aircraft == 'B78X':
            ffph = 2534
            knots = 488

        #Set Fuel
        if load_fuel == 1:
                        
            #The formula for A320 we use is ((Distance / Knots) * Fuel Flow Per hour) + Fuel flow per hour, with the addition being 1 hour of reserve.    
            fuel = round(((distance / knots) * ffph) + ffph)
            
            pyautogui.click(x=1246, y=519)
            pyautogui.sleep(0.1)
            pyautogui.write(str(fuel))
            pyautogui.sleep(0.1)
        else:
            #Select don't load fuel
            pyautogui.click(x=600, y=554)
        
        
        #Set whether crew sleep
        # Divide the flight distance by the speed and then add 36 minutes of mucking about
        hoursWorked += (distance / knots) + 0.6
        print('Current hours worked:' + str(round(hoursWorked, 1)))

        
        if i+1 < len(lines):
            # get the distance for the next job
            next_distance = int(round(float(lines[i+1].strip().split(',')[4])))
            next_hours = (next_distance / knots) + 0.6
            print('Next flight hours: ' + str(next_hours))
            print('Predicted next flight hours: ' + str(next_hours + hoursWorked))
        else:
            next_hours = 14 #To force a crew rest before starting the new work order.

        if hoursWorked + next_hours > 13 and rest_crew == 1:
            hoursWorked = 0
            pyautogui.click(x=1917, y=550)



        # If hours worked is over 11 (which gives a 2 hour gap of fucking about) then rest the crew
        #if hoursWorked > 11 and rest_crew == 1:
        #    hoursWorked = 0
        #    pyautogui.click(x=1917, y=550)

        #Add a new leg
        pyautogui.click(x=130, y=463)
        pyautogui.sleep(0.2)

#Select Delete Leg
pyautogui.click(x=263, y=466)
pyautogui.sleep(0.2)

#Select Yes
pyautogui.click(x=1874, y=1196)
pyautogui.sleep(0.2)
#input("Done! Press Enter to exit...")
