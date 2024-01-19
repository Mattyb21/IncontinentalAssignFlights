import pyautogui
import pytesseract
from PIL import Image
import time

# Set the path to the tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Change this to your Tesseract path

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
            if occurrence_count == 1:  # Check if it's the second occurrence
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
        print(f"Second occurrence of '{word}' not found on screen.")
        
        
pyautogui.click(x=2786, y=326)
pyautogui.sleep(1)


click_second_occurrence('4,386,569.50')

# Wait a bit before the program ends
time.sleep(20)
