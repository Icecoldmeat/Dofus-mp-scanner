"""This code is executed before starting any other code"""
import sys

import pyautogui
from dotenv import load_dotenv
from definitions import DOTENV_PATH, SOURCE_PATH
from marketplace import MarketScanner

# load enviromental variables
load_dotenv(DOTENV_PATH)
sys.path.append(SOURCE_PATH)

print("Env files loaded!")

#screenshot = pyautogui.screenshot()
#screenshot.save("screenshot.png")
mpscanner = MarketScanner()
#mpscanner.moveAndClick()
#mpscanner.save(1)
mpscanner.ocrEasyOcr()