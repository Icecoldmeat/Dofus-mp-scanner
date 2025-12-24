import csv
import math
from typing import Union, Any
import glob

from enum import Enum
import pyautogui
import time
import pygetwindow
import random
from humancursor import SystemCursor
import mouse
import pyscreenshot as ImageGrab
from pyrect import Box
from datetime import datetime, timezone
import easyocr
import os
from PIL import Image
import re

class MouseMover:

    def move_mouse_natural(self,x1, y1, x2, y2, max_step=15):
        """
        Move mouse from (x1, y1) to (x2, y2) in a human-like, natural way.
        Short movements remain small and jittery; long movements are curved and smooth.

        max_step: maximum pixels per movement step (controls speed)
        """
        # Calculate distance
        distance = math.hypot(x2 - x1, y2 - y1)

        # If movement is very short, use tiny jittery linear steps
        if distance < 50:
            steps = max(int(distance / 2), 1)  # smaller steps for precision
            for i in range(1, steps + 1):
                t = i / steps
                nx = x1 + (x2 - x1) * t + random.uniform(-1, 1)
                ny = y1 + (y2 - y1) * t + random.uniform(-1, 1)
                mouse.move(int(nx), int(ny))
                time.sleep(random.uniform(0.03, 0.06))  # slower, natural movement
            return

        # For longer movements, use a curved Bezier path
        # Random control point
        cx = (x1 + x2) / 2 + random.randint(-100, 100)
        cy = (y1 + y2) / 2 + random.randint(-100, 100)

        # Quadratic Bezier interpolation
        def bezier(t, p0, p1, p2):
            return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2

        steps = max(int(distance / max_step), 1)

        for i in range(1, steps + 1):
            t = i / steps
            nx = bezier(t, x1, cx, x2) + random.uniform(-2, 2)
            ny = bezier(t, y1, cy, y2) + random.uniform(-2, 2)
            mouse.move(int(nx), int(ny))

            # Speed modulation: start slow, fast in middle, slow at end
            speed = 0.002 + 0.005 * (1 - math.cos(t * math.pi))
            time.sleep(speed)

class MarketScanner:
    MP_ITEM_BOX_WIDTH = 390
    MP_ITEM_BOX_HEIGHT_FROM_MIDDLE = 20
    MP_ITEMS_REGION = (688, 24, 731, 1017)
    MP_ITEM_SALE_BOX_REGION = (154, 156, 421+154, 348+156)
    MP_VALIDATE_NEW_ITEMS_REGION = (895, 287, 281+895, 575+287)

    def __init__(self):
        self.i = 0
        self.cursor = SystemCursor()
        self.mouse_mover = MouseMover()
        self.reader = easyocr.Reader(['en'])
        self.image_text = None

        date = datetime.now().strftime("%Y%m%d")
        time = datetime.now().strftime("%H%M%S")
        path = f"cache/items/{date}/{time}"
        os.makedirs(path, exist_ok=True)
        self.file_output = path

    def startup(self):
        window = pygetwindow.getWindowsWithTitle('Littlelientje')[0]
        window.maximize()
        window.activate()
        time.sleep(1)

    def retrieve_marketplace_images(self) ->  None:
        file_path = f"cache/validate.png"
        im = ImageGrab.grab(bbox=self.MP_VALIDATE_NEW_ITEMS_REGION)

        im.save(file_path)
        image_text = self.reader.readtext(file_path, detail=0)
        if self.image_text is not None and self.image_text == image_text:
            print(f"No new auctions found, exiting code")
            exit()

        self.image_text = image_text

        locations = self._locate_all('images/kamas_2.png', confidence=0.82)
        amount_of_time = random.uniform(0.2, 0.44)
        self.locate_image(amount_of_time, locations)
       # scroll_mouse_wheel = random.randint(5,7)
        for x in range(random.randint(5,7)):
            mouse.wheel(-1)
            time.sleep(random.uniform(0.0020, 0.040))


        self.retrieve_marketplace_images()

    def locate_image(self, amount_of_time: float, locations: list[Any]):
        if random.randint(0, 100) < 30:
            length_list = len(locations)
            random_movement = random.randint(1, length_list)
            locations = self._move_element(locations, random_movement, random_movement- 1)

        for i, location in enumerate(locations):
            x, y = self._boxCalculator(location)
            if i == len(locations) - 1:
                x, y = self._boxCalculator(location,True)

            if i == 0:
                x, y = self._boxCalculator(location,False,True)


            if random.randint(0, 100) < 2:
                time.sleep(random.uniform(2, 10))

            if random.randint(0, 100) < 30:
               # self.cursor.move_to([x, y], duration=amount_of_time, steady=True)
                self.cursor.move_to([x, y])
            else:
                current_x, current_y = pyautogui.position()
                self.mouse_mover.move_mouse_natural(current_x,current_y,x,y)
                #mouse.move(x, y, duration=amount_of_time)

            mouse.click()
            self.save(self.i)
            amount_of_time = random.uniform(0.19, 0.32)
        #    x, y = pyautogui.position()

        #    time.sleep(random.uniform(0.20, 0.40))
        #    print(f"Mouse position: x={x}, y={y}")

            self.i = self.i + 1
            print(f"This is cycle {self.i}")

    def _move_element(self, lst: list, from_index: int, to_index: int):
        """
        Move the element at from_index to be just before to_index.
        """
        # Remove the element
        elem = lst.pop(from_index)

  #      # If removing an element before the target, the target index shifts left by 1
  #      if from_index < to_index:
  #          to_index -= 1

        # Insert the element at the new position
        lst.insert(to_index, elem)
        return lst

    def _boxCalculator(self,location: Box, last: bool = False, first = False):
        x = location.left
        y = location.top

        x_randomized = random.randint(x - self.MP_ITEM_BOX_WIDTH,x)
        y_randomized = random.randint(y - self.MP_ITEM_BOX_HEIGHT_FROM_MIDDLE, y + self.MP_ITEM_BOX_HEIGHT_FROM_MIDDLE)
        if last:
            print('hit the last one!')
            y_randomized = random.randint(y - self.MP_ITEM_BOX_HEIGHT_FROM_MIDDLE,y )

        if first:
            print('hit the first one!')
            y_randomized = random.randint(y ,
                                          y + self.MP_ITEM_BOX_HEIGHT_FROM_MIDDLE)

        return x_randomized, y_randomized

    def _locate_all(self,path, confidence=0.9, distance=10):
        distance = pow(distance, 2)
        elements = []
        for element in pyautogui.locateAllOnScreen(path, confidence=confidence, grayscale=False, region=self.MP_ITEMS_REGION):
            if all(map(lambda x: pow(element.left - x.left, 2) + pow(element.top - x.top, 2) > distance, elements)):
                elements.append(element)
        return elements

    def save(self,i: int) -> None:
        window = pygetwindow.getWindowsWithTitle('Littlelientje')[0]
        window.maximize()
        window.activate()

        # part of the screen
        im = ImageGrab.grab(bbox=self.MP_ITEM_SALE_BOX_REGION)

        im.save(f'{self.file_output}/{i}.png')

class ProductModel:
    name: str
    price_type: str
    price: int
    creation_date: datetime
    file_name: str

class Scraper:

    def scrape(self, row: list, file: str):
        if len(row) == 0:
            return

        length = len(row)
        name = None
        average_price = None
        prices = None
        for i, item in enumerate(row):
            if 'Lvl' in item['value']:
                name = row[0:i]

            if 'price:' in item['value']:
                average_price = item

            if 'Pack' in item['value']:
                prices = row[i:length]

        name = self.clean_name(name)
        average_price = self.clean_average_price(average_price)
        pack_price = self.clean_price(prices)
        item_prices = []
        for key, price in pack_price.items():
            product_model = ProductModel()
            product_model.name = name.replace('WV','W')
            product_model.price_type = str(key).replace(',','')
            product_model.price = price
            product_model.file_name = file
            product_model.creation_date = datetime.now()

            item_prices.append(product_model)

        product_model = ProductModel()
        product_model.name = name.replace('WV','W')
        product_model.price_type = 'average'
        product_model.price = average_price
        product_model.file_name = file
        product_model.creation_date = datetime.now()

        item_prices.append(product_model)

        return item_prices



    def clean_name(self, names: list) -> str:
        if len(names) == 1:
            return names[0]['value']

        filtered_names = []
        for name in names:
            # The image all have the same dimensions item name starts at 44
            if int(name['y']) < 50:
                filtered_names.append(name)
        sorted_data = sorted(filtered_names, key=lambda d: d['x'])

        return " ".join(v["value"] for v in sorted_data)


    def clean_average_price(self, average_price: dict) -> int:
        is_number, number = self.find_number_with_comma(average_price['value'])

        return number

    def clean_price(self, prices: list) -> dict: #TODO THIS IS ONLY FOR RESOURCES
        product_prices = []
        pack = []
        for price in prices:
            if price['value'] in ['Pack','Price']:
                continue

            if 'X' in price['value'] or 70 <= int(price['x']) <= 90:
                pack.append(price['value'].replace('X',''))
                continue

            is_number, number = self.find_number_with_comma(price['value'])
            if is_number:
                product_prices.append(number)
                continue

        if len(pack) != len(product_prices):
            packs = [1,10,100,1000]
            recleaned_prices = [x for x in product_prices if x not in packs]
            pack = packs[:len(product_prices)]
            if len(pack) == len(recleaned_prices):
                product_prices = recleaned_prices

            if len(product_prices) > 4:
                raise Exception('product_prices cant be this high')




        pack_price = dict(zip(pack, product_prices))
        return pack_price


    def find_number_with_comma(self, s: str):
        """
        Checks if the string contains a number. Numbers can have an optional comma as a decimal separator.

        Returns:
            (bool, float or None):
                - True and the number value if a number is found
                - False and None if no number is found

        Matches examples:
            "123"        -> 123.0
            "45,67"      -> 45.67
            "Price: 1,99"-> 1.99

        Does NOT match:
            "abc"        -> No number
            ",45"        -> Invalid, missing integer part before comma
            "12,"        -> Invalid, missing fractional part after comma
        """
        s = s.replace(',','')
        match = re.search(r'\d+(,\d+)?', s)
        if match:
            # Replace comma with dot to convert to float
            number_str = match.group()
            return True, float(number_str)
        return False, None




class ScraperManager:

    def __init__(self) -> None:
        self.reader = easyocr.Reader(['en'], gpu=True)
        self.scrape = Scraper()

    def get_sales(self):
        list_of_files = glob.glob("cache/items/**/*.png", recursive=True)

        for file in list_of_files:
            result = self.reader.readtext(file, detail=1, batch_size=5, blocklist='*#')
            if result is None or len(result) == 0:
                continue

            converted_result = self.convert(result)
            scraped_result = self.scrape.scrape(converted_result, file)
            self.write_to_file(scraped_result)

    def get_sale(self,file : str):

        result = self.reader.readtext(file, detail=1, batch_size=5, blocklist='*#')
        converted_result = self.convert(result)
        scraped_result = self.scrape.scrape(converted_result, file)
        print(scraped_result)



    def write_to_file(self, products: list):
        with open("cache/products.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=';')

            # If file is empty, write header first
            if file.tell() == 0:
                writer.writerow(["name", "price", "price_type","file_path","creation_date"])

            # Write rows
            try:
                for product in products:
                    writer.writerow([product.name, product.price, product.price_type,product.file_name,product.creation_date])
            except Exception as e:
                print(e)

    def convert(self, result: list) -> list:
        all_values = []
        for item in result:
            values = {
                'value': item[1],
                'x': int(item[0][0][0]),
                'y': int(item[0][0][1]),
            }
            all_values.append(values)

        return all_values



manager = ScraperManager()
manager.get_sale('cache/items\\20251222\\215330\\0.png')
manager.get_sales()
###
#  Id:
#  Name:
#  Price_type: [average,1,10,100,1000]
#  Price :
##

