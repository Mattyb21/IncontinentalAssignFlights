import pyautogui
import pyperclip

currentPayload = pyperclip.paste().split("\t")
currentField = 0



while currentField < 14:
    print('Field ' + str(currentField) + ': ' + currentPayload[currentField])
    print('Type is: ' + str(type(currentPayload[currentField])))
    currentField += 1

print("******")
print(float(currentPayload[10].split()[0]))

if float(currentPayload[10].split()[0]) < 30:
    print("TRUE")
