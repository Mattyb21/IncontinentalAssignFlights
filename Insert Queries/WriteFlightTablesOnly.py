import pyautogui
import pyperclip
from screeninfo import get_monitors
import pandas as pd
import shutil
import csv

input("This is the 4k screen version, with the program maximised. Check this and then hit Enter..")

#Saving all the data

# define the names of the files to read from
filenames = ['A320.csv', 'B78X.csv', 'TBM9.csv', 'B78X1.csv', 'B78X2.csv']

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


print("All records processed.")
input()
