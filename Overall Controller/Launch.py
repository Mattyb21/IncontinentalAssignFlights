import subprocess
import pygetwindow as gw
import pyautogui
import time

# Launch the application
onair_appref_ms_path = r'C:\Users\Server\Desktop\OnAir Company.appref-ms'
subprocess.Popen(f'cmd /c start "" "{onair_appref_ms_path}"', shell=True)

# Wait for a moment to allow the application to start
time.sleep(5)

# Try to find the window
try:
    # You need to know the title of the window to find it
    window_title = "OnAir Airline Manager" 
    onair_window = gw.getWindowsWithTitle(window_title)[0]  # Get the first window with the title

    if onair_window:
        # Maximize the window
        onair_window.maximize()
        print("Window maximized.")
    else:
        print("Window not found.")
except Exception as e:
    print(f"An error occurred: {e}")

time.sleep(20)


#Click Resume
pyautogui.click(x=2231, y=1573)
time.sleep(25)

#Click VA Ops
pyautogui.click(x=627, y=55)
time.sleep(1)

#Click VA
pyautogui.click(x=627, y=175)
time.sleep(50)
#Real wake up call that onair is slow as fuck

#Click Aircaft Selection
pyautogui.click(x=1820, y=63)
time.sleep(5)