import pyautogui
import time

# Wait for 5 seconds
time.sleep(5)

# Get and print the current mouse position
current_mouse_position = pyautogui.position()
print(f"Current mouse position: {current_mouse_position}")
