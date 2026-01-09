import csv
import os
import shutil
import glob
from dataclasses import dataclass
from datetime import datetime, timezone
from time import sleep
from typing import Union, Any

import cv2
import easyocr
import re

import numpy as np
from matplotlib import pyplot as plt
from sympy import false

from definitions import UNPROCESSED_ITEMS_PATH, CACHE_PATH, ROOT
from marketplace_boxes import MarketPlaceScannerBoxes
from repository.mysql import DofusPriceModel, ExternalDofusPriceRepository


@dataclass
class PricePartModel:
    price: int
    price_type: str


class ScraperUtility:

    @staticmethod
    def find_number_with_comma(s: str):
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
        s = s.replace(',', '')
        match = re.search(r'\d+(,\d+)?', s)
        if match:
            # Replace comma with dot to convert to float
            number_str = match.group()
            return True, float(number_str)
        return False, None

    @staticmethod
    def folder_path_to_creation_date(file: str) -> datetime:
        parts_creation_date = file.split('/')
        date_str = parts_creation_date[-3]
        time_str = parts_creation_date[-2]
        creation_date = datetime.strptime(date_str + time_str, '%Y%m%d%H%M%S')
        return creation_date


class ScraperPriceCleaner:

    def __init__(self, scanner_boxes: MarketPlaceScannerBoxes):
        self.scanner_boxes = scanner_boxes

    def clean_price(self, prices: Union[None, list], file: str) -> list[
        PricePartModel]:
        if prices is None:
            return []

        grouped_prices = self._group_prices_by_y(prices)
        pack, packless_items = self._get_pack(grouped_prices)
        concat_values = self._concat_items(packless_items)

        product_prices = self._get_prices(concat_values)

        pack, product_prices = self.fill_in_missing_packs(file, pack, product_prices)

        price_part_models = [PricePartModel(a, b) for a, b in zip(product_prices, pack)]

        return price_part_models

    def fill_in_missing_packs(self, file: str, pack: list[Any],
                              product_prices: list[Any]) -> tuple[list[Any], list[int]]:
        if len(pack) != len(product_prices):
            packs = [1, 10, 100, 1000]
            recleaned_prices = [x for x in product_prices if x not in packs]
            if pack.count('1') > 1 and pack.count('10') == 0 and pack.count('100') == 0 and pack.count('1000') == 0:
                packs = [1, 1, 1, 1]

            pack = packs[:len(product_prices)]
            if len(pack) == len(recleaned_prices):
                product_prices = recleaned_prices

            if len(product_prices) > 4:
                print(file)
                raise Exception('product_prices cant be this high')

        return pack, product_prices

    def _get_prices(self, concat_values: list[Any]) -> list[Any]:
        product_prices = []
        for price in concat_values:
            price_value = price['value']
            clean_price = price_value.replace('o', '0').replace('O', '0').replace(',', '').replace(' ', '')
            is_number, number = ScraperUtility.find_number_with_comma(clean_price)
            if is_number:
                product_prices.append(number)
        return product_prices

    def _concat_items(self, packless_items: list[Any]):
        concat_values = []
        for packless_item in packless_items:
            result = {
                'value': ''.join(item['value'] for item in packless_item),
                'x': packless_item[0]['x'],
                'y': packless_item[0]['y']
            }

            concat_values.append(result)

        return concat_values

    def _get_pack(self, grouped_prices: list[dict]) -> tuple[list[Any], list[Any]]:
        pack = []
        packless_items = []
        for group in grouped_prices:
            might_be_prices = []
            for might_be_pack in group:
                if int(might_be_pack['x']) < self.scanner_boxes.mp_item_sale_box_pack_image_end_x:
                    continue

                pack_x_start = self.scanner_boxes.mp_item_sale_box_pack_image_end_x
                pack_x_end = self.scanner_boxes.mp_item_sale_box_pack_image_pack_x_end
                might_be_pack['value'] = might_be_pack['value'].replace('o', '0')
                if 'X' in might_be_pack['value'] or pack_x_start <= int(might_be_pack['x']) <= pack_x_end:
                    pack.append(might_be_pack['value'].replace('X', '').replace('x', ''))
                    continue

                if int(might_be_pack['x']) < self.scanner_boxes.mp_item_sale_box_pack_image_end_star_x:
                    continue

                might_be_prices.append(might_be_pack)
            if len(might_be_prices) > 0:
                packless_items.append(might_be_prices)

        return pack, packless_items

    def _group_prices_by_y(self, data: list[dict]) -> list[dict]:
        tolerance = 10

        # Sort by y so nearby values are processed together
        data = sorted(data, key=lambda d: d["y"])

        groups = []

        for item in data:
            if item['value'] in ['Pack', 'Price', 'BUY']:
                continue

            placed = False
            for group in groups:
                # compare with the first y-value in the group
                if abs(item["y"] - group[0]["y"]) <= tolerance:
                    group.append(item)
                    placed = True
                    break

            if not placed:
                groups.append([item])

        for group in groups:
            group.sort(key=lambda d: d["x"])

        return groups


class Scraper:

    def __init__(self, scanner_boxes: MarketPlaceScannerBoxes):
        self.scanner_boxes = scanner_boxes
        self.price_cleaner = ScraperPriceCleaner(scanner_boxes)

    def scrape(self, row: list, file: str) -> Union[None, list[DofusPriceModel]]:
        if len(row) <= 3:
            return None

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
        pack_price = self.price_cleaner.clean_price(prices, file)
        pack_price.insert(0, average_price)
        item_prices = []
        file = file[file.find('cache'):].replace('\\', '/').replace('//', '/')

        creation_date = ScraperUtility.folder_path_to_creation_date(file)
        i = 1
        for price_part_model in pack_price:
            price_model = self.map(creation_date, file, price_part_model.price_type, name, price_part_model.price, i)
            item_prices.append(price_model)
            i = i + 1

        return item_prices

    def map(self, creation_date: datetime, file: str, price_type, name: str, price,
            auction_number: int) -> DofusPriceModel:
        price_model = DofusPriceModel()
        price_model.name = name.replace('WV', 'W')

        price_type_cleaned = str(price_type).replace(',', '').replace('x', '').replace('X', '').replace('o',
                                                                                                        '0').replace(
            'O', '0').strip()
        if price_type_cleaned == '' or price_type_cleaned is None:
            price_type_cleaned = 1
        price_model.price_type = price_type_cleaned
        price_model.price = price
        price_model.auction_number = auction_number
        price_model.image_file_path = file
        price_model.creation_date = creation_date
        price_model.update_date = creation_date
        return price_model

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

    def clean_average_price(self, average_price: dict) -> PricePartModel:
        is_number, number = ScraperUtility.find_number_with_comma(average_price['value'])

        return PricePartModel(number, 'average')


class ScraperManager:

    def __init__(self, scraper: Scraper) -> None:
        self.reader = easyocr.Reader(['en'], gpu=True)
        self.scrape = scraper
        self.repo = ExternalDofusPriceRepository()

    def get_sales(self) -> None:
        path = f"{UNPROCESSED_ITEMS_PATH}/**/*.png"
        list_of_files = glob.glob(path, recursive=True)
        count = len(list_of_files)

        sleep(2)  # make sure images are saved
        i = 0
        for file in list_of_files:
            image = self.preprocess(file)
            result = self.reader.readtext(image, detail=1, batch_size=50, blocklist='*#')
            if result is None or len(result) <= 3:
                self.move_file_to_processed(file)
                continue

            converted_result = self.convert(result)
            scraped_results = self.scrape.scrape(converted_result, file)

            for scraped_result in scraped_results:
                self.repo.insert(scraped_result)
            # self.write_to_file(scraped_result)
            self.move_file_to_processed(file)

            i = i + 1
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Inserted {i} of {count} - {file}")


    def get_sale(self, file: str) -> Union[None, list[DofusPriceModel]]:
        path = ROOT + file
        image = self.preprocess(path)
        result = self.reader.readtext(image, detail=1, batch_size=5, blocklist='*#')

        converted_result = self.convert(result)
        scraped_result = self.scrape.scrape(converted_result, path)
        return scraped_result

    def preprocess2(self, file_path: str):
        image = cv2.imread(file_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        bw = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            5
        )
        return bw

    def preprocess(self, file_path: str):
        image = cv2.imread(file_path)
        b, g, r = cv2.split(image)
        r_boosted = cv2.multiply(r, 1.5)
        r_boosted = np.clip(r_boosted, 0, 255).astype(np.uint8)

        gray_red_emphasized = cv2.addWeighted(r_boosted, 0.6, b, 0.2, 0)
        gray_red_emphasized = cv2.addWeighted(gray_red_emphasized, 1.0, g, 0.2, 0)

        return gray_red_emphasized

    def move_file_to_processed(self, image_file_path: str):
        if image_file_path is None:
            raise Exception('image_file_path cannot be None')

        if 'unprocessed' not in image_file_path:
            raise Exception('folder name unprocessed should be in path')

        processed_path = image_file_path.replace('unprocessed', 'processed')
        os.makedirs(os.path.dirname(processed_path), exist_ok=True)
        shutil.move(image_file_path, processed_path)

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
