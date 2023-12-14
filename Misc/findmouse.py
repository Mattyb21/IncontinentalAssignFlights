import pyautogui
import keyboard
import pyperclip

screen_width, screen_height = pyautogui.size()
print(f"Screen size: {screen_width}x{screen_height}")

def copy_to_clipboard(x, y):
    formatted_str = f'pyautogui.click(x={x}, y={y})'
    pyperclip.copy(formatted_str)
    return formatted_str

try:
    while True:
        x, y = pyautogui.position()
        position_str = f'X: {str(x).rjust(4)} Y: {str(y).rjust(4)}'
        print(position_str, end='')
        print('\b' * len(position_str), end='', flush=True)

        # Check for F15 keypress
        if keyboard.is_pressed('F15'):
            formatted_str = copy_to_clipboard(x, y)
            print(f'\nCoordinates copied to clipboard: {formatted_str}')

except KeyboardInterrupt:
    print('\n')
