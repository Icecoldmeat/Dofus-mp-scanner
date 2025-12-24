import pyautogui
import keyboard

print("Press F1 to get mouse coordinates. Press ESC to quit.")

while True:
    if keyboard.is_pressed('F1'):
        x, y = pyautogui.position()
        print(f"Mouse position: x={x}, y={y}")
        keyboard.wait('F1', suppress=True)  # prevent spam while holding key

    if keyboard.is_pressed('esc'):
        print("Exiting...")
        break

