import pytesseract
from PIL import Image
#
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows example
#
#image_path = "cache/pictures/Capture.PNG"
#image = Image.open(image_path)
#extracted_text = pytesseract.image_to_string(image)
#print(extracted_text)
import glob

import pyautogui
import time
import pygetwindow
import random
from humancursor import SystemCursor
import mouse
import pyscreenshot as ImageGrab
from pyrect import Box
import easyocr

class MarketScanner:

    def __init__(self):
        pass

    def moveAndClick(self) ->  None:
        cursor = SystemCursor()
      #  png = 'Dofus_fake'
        window = pygetwindow.getWindowsWithTitle('Littlelientje')[0]
        window.maximize()
        window.activate()
    #    window.resizeTo(1200, 1000)
    #    window.moveTo(0, 0)
        time.sleep(1)
      #  locations = pyautogui.locateAllOnScreen('images/kamas_2.png', confidence=0.82, grayscale=False, region=(688, 24, 731, 1017))
        locations = self._locate_all('images/kamas_2.png', confidence=0.82)
        i = 0
        amountOfTime = random.uniform(0.4, 0.84)
        for location in locations:
            x,y = self._boxCalculator(location)
            if random.randint(0,100) < 20:
                cursor.move_to([x, y], duration=amountOfTime,steady=True)

            else :
                mouse.move(x, y, duration=amountOfTime)

            mouse.click()
            self.save(i)
            amountOfTime = random.uniform(0.10, 0.49)
            x, y = pyautogui.position()


       #     pyautogui.click()
       #     pyautogui.locateAllOnScreen('images/kamas.png', confidence=0.93, grayscale=False, region=(0, 0, 1920, 1080))
            time.sleep(random.uniform(0.20, 0.40))
            print(f"Mouse position: x={x}, y={y}")

            i = i + 1
            print(f"This is cycle {i}")



    def _boxCalculator(self,location: Box):

        x = location.left
        y = location.top

        xrandomized = random.randint(x - 400,x)
        yrandomized = random.randint(y - 20, y + 20)

        return xrandomized, yrandomized

    def _locate_all(self,path, confidence=0.9, distance=10):
        distance = pow(distance, 2)
        elements = []
        for element in pyautogui.locateAllOnScreen(path, confidence=confidence, grayscale=False, region=(688, 24, 731, 1017)):
            if all(map(lambda x: pow(element.left - x.left, 2) + pow(element.top - x.top, 2) > distance, elements)):
                elements.append(element)
        return elements

    def save(self,i: int) -> None:
        window = pygetwindow.getWindowsWithTitle('Littlelientje')[0]
        window.maximize()
        window.activate()

        # part of the screen
        im = ImageGrab.grab(bbox=(154, 156, 421+154, 348+156))

        # to file
        im.save(f'cache/20251221/{i}.png')

    def ocrTesseract(self) -> None:
        listOfFiles = glob.glob("cache/20251221/*")
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        for file in listOfFiles:
            image = Image.open(file)
            extracted_text = pytesseract.image_to_string(image)
            print(extracted_text)

    def ocrEasyOcr(self) -> None:

        reader = easyocr.Reader(['en'])

        listOfFiles = glob.glob("cache/20251221/*")
     #   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        for file in listOfFiles:
            result = reader.readtext(file,detail=0)
            print(result)
