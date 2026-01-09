
from typing import Any


import mouse
import pyautogui
import time
import pygetwindow
import random
from humancursor import SystemCursor

from definitions import UNPROCESSED_ITEMS_PATH, CACHE_PATH, IMAGE_PATH
from marketplace_boxes import MarketPlaceScannerBoxes
from mouse_mover import NaturalMouseMover
import pyscreenshot as ImageGrab
from pyrect import Box
from datetime import datetime
import easyocr
import os

class MarketScanner:

    def __init__(self,  scanner_boxes: MarketPlaceScannerBoxes):
        self.i = 0
        self.cursor = SystemCursor()
        self.reader = easyocr.Reader(['en'])
        self.image_text = None
        self.scanner_boxes = scanner_boxes

        date = datetime.now().strftime("%Y%m%d")
        time = datetime.now().strftime("%H%M%S")
        path = f"{UNPROCESSED_ITEMS_PATH}/{date}/{time}"
        os.makedirs(path, exist_ok=True)
        self.file_output = path

    def startup(self):
        window = pygetwindow.getWindowsWithTitle('Littlelientje')[0]
        window.maximize()
        window.activate()
        time.sleep(1)

    def retrieve_marketplace_images(self) ->  None:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Start Retrieving")
        file_path = f"{CACHE_PATH}/validate.png"

        #time.sleep(0.3)


        im = ImageGrab.grab(bbox=self.scanner_boxes.mp_validate_new_items_region)
        im.save(file_path)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Saved Marketplace image")

        image_text = self.reader.readtext(file_path, detail=0)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - saved {self.image_text}")
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - current {image_text}")
        if self.image_text is not None and self.image_text == image_text:
            print(f"No new auctions found, exiting code")
            exit()

        self.image_text = image_text
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Checked image")
        locations = self._locate_all(f'{IMAGE_PATH}/kamas_2.png', confidence=0.82)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Located Images")
        self.locate_image(locations)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - moved to all images and clicked")
       # scroll_mouse_wheel = random.randint(5,7)
        for x in range(random.randint(5,7)):
            mouse.wheel(-1)
            time.sleep(random.uniform(0.0020, 0.040))

        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - End, back to beginning")
        self.retrieve_marketplace_images()


    def locate_image(self, locations: list[Any]):
        print(f"-- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Start moving")
        if random.randint(0, 100) < 30:
            length_list = len(locations)
            random_movement = random.randint(1, length_list)
            locations = self._move_element(locations, random_movement, random_movement- 1)
        print(f"-- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Added randomize movement chuncks")
        for i, location in enumerate(locations):
            x, y = self._boxCalculator(location)
            if i == len(locations) - 1:
                x, y = self._boxCalculator(location,True)

            if i == 0:
                x, y = self._boxCalculator(location,False,True)


       #     if random.randint(0, 100) < 2:
       #         time.sleep(random.uniform(2, 10))

            print(f"-- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - start actual movement")
            current_x, current_y = pyautogui.position()
            #self.mouse_mover.move_mouse_natural(current_x,current_y,x,y)
            natural_mover = NaturalMouseMover(speed=3)
            natural_mover.move(current_x,current_y,x,y)
            print(f"-- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - moved to spot")
            #mouse.move(x, y, duration=amount_of_time)

            mouse.click()
            print(f"-- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - clicked spot")
            self.save(self.i)
            print(f"-- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - saved spot")
            amount_of_time = random.uniform(0.19, 0.32)
        #    x, y = pyautogui.position()

        #    time.sleep(random.uniform(0.20, 0.40))
        #    print(f"Mouse position: x={x}, y={y}")

            self.i = self.i + 1
            print(f"-- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -  This is cycle {self.i}")

    def _move_element(self, lst: list, from_index: int, to_index: int):
        """
        Move the element at from_index to be just before to_index.
        """
        # Remove the element
        try:
            elem = lst.pop(from_index)

  #      # If removing an element before the target, the target index shifts left by 1
  #      if from_index < to_index:
  #          to_index -= 1

        # Insert the element at the new position
            lst.insert(to_index, elem)
        except:
            print(lst,from_index,to_index)
            print('fuck')

        return lst

    def _boxCalculator(self,location: Box, last: bool = False, first = False):
        x = location.left
        y = location.top

        x_randomized = random.randint(x -  self.scanner_boxes.mp_item_box_width,x)
        y_randomized = random.randint(y - self.scanner_boxes.mp_item_box_height_from_middle, y + self.scanner_boxes.mp_item_box_height_from_middle)
        if last:
            print('hit the last one!')
            y_randomized = random.randint(y -  self.scanner_boxes.mp_item_box_height_from_middle,y - 3 )

        if first:
            print('hit the first one!')
            y_randomized = random.randint(y + 3 ,
                                          y +  self.scanner_boxes.mp_item_box_height_from_middle)

        return x_randomized, y_randomized

    def _locate_all(self,path, confidence=0.9, distance=10):
        distance = pow(distance, 2)
        elements = []
        for element in pyautogui.locateAllOnScreen(path, confidence=confidence, grayscale=False, region=self.scanner_boxes.mp_items_kamas_region):
            if all(map(lambda x: pow(element.left - x.left, 2) + pow(element.top - x.top, 2) > distance, elements)):
                elements.append(element)
        return elements

    def save(self,i: int) -> None:
        window = pygetwindow.getWindowsWithTitle('Littlelientje')[0]
        window.maximize()
        window.activate()

        # part of the screen
        im = ImageGrab.grab(bbox=self.scanner_boxes.mp_item_sale_box_region)

        im.save(f'{self.file_output}/{i}.png')


###
#  Id:
#  Name:
#  Price_type: [average,1,10,100,1000]
#  Price :
##

