"""This code is executed before starting any other code"""
import threading
import keyboard
from marketplace import MarketScanner
from marketplace_boxes import average_text_box

stop_script = False  # flag to signal main loop to stop
def monitor_f2():
    global stop_script
    keyboard.wait("F2")  # blocks until F2 is pressed
    stop_script = True
    print("F2 pressed. Exiting...")

# Start the F2 monitor thread
threading.Thread(target=monitor_f2, daemon=True).start()

print("Main logic running. Press F2 to exit.")

# Main logic loop runs constantly
while not stop_script:
    mpscanner = MarketScanner(average_text_box)
    mpscanner.startup()
    mpscanner.retrieve_marketplace_images()

#print("Script exited.")
#screenshot = pyautogui.screenshot()
#screenshot.save("screenshot.png")

#mpscanner.save(1)
#mpscanner.ocrEasyOcr()

