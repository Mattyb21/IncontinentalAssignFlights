import pyautogui
import pyperclip
import pandas as pd

a = input('Please ensure you have gone to pending jobs and selected the FBO Queries tab. ALSO SORT BY PAY. Press enter once you have ...')


# Load the JobsToTake.csv file into a DataFrame
jobs_df = pd.read_csv('JobsToTake.csv')

# Load the FBOs.csv file into a DataFrame
fbos_df = pd.read_csv('FBOs.csv')

# Get the values in the first field (field 0) from the JobsToTake.csv file
jobs_FBOID = set(jobs_df.iloc[:, 0].values)

#Clicking Select FBO
pyautogui.click(x=243, y=300)

# Go through each record in the fourth field (field 3) of the FBOs.csv file
for index, row in fbos_df.iterrows():
    FBOs = row.iloc[3]  # Access the value in the fourth field (field 3)

    # Check if the value exists in the first field (field 0) of the JobsToTake.csv file
    if FBOs in jobs_FBOID:
        #Select the FBO
        pyautogui.press('enter')

        #Wait ages for it to load
        pyautogui.sleep(20)

        #Sel cargo field
        pyautogui.click(x=662, y=464)
        pyautogui.sleep(0.2)

        #Copy the row
        pyautogui.hotkey('ctrl', 'c')
        pyautogui.sleep(0.2)

        current_job = pyperclip.paste().split("\t")

        fuckedLoop = 0

        while fuckedLoop < 150:

            for job_index, job_row in jobs_df.iterrows():
                if job_row.iloc[0] == FBOs and abs(float(job_row.iloc[1].replace(',', '')) - float(current_job[16].replace(',', ''))) <= 1:
                    #We do the action here to take the job
                    #Headed left to the take button
                    pyautogui.press('left')
                    pyautogui.sleep(0.1)

                    pyautogui.press('left')
                    pyautogui.sleep(0.1)

                    pyautogui.press('left')
                    pyautogui.sleep(0.1)

                    pyautogui.press('left')
                    pyautogui.sleep(0.1)

                    pyautogui.press('left')
                    pyautogui.sleep(0.1)

                    pyautogui.press('left')
                    pyautogui.sleep(0.1)

                    #Tab to highlight button
                    pyautogui.press('tab')
                    pyautogui.sleep(0.1)

                    #Enter to take job
                    pyautogui.press('enter')
                    #Long sleep for load screen
                    pyautogui.sleep(5)

                    #click back on cargo1
                    pyautogui.click(x=662, y=464)
                    pyautogui.sleep(0.2)

                    break
            
            #next record 
            pyautogui.press('down')
            pyautogui.sleep(1)

            #Copy the row
            pyautogui.hotkey('ctrl', 'c')
            pyautogui.sleep(0.2)

            if pyperclip.paste().split("\t") == current_job:
                #There's probably no more jobs, time to move to the next job
                #selecting FBO box
                pyautogui.click(x=243, y=300)
                pyautogui.sleep(0.2)
                break

            current_job = pyperclip.paste().split("\t")
            fuckedLoop += 1
    
    #Next FBO
    pyautogui.press('down')
    pyautogui.sleep(0.4)

print('Completed')

