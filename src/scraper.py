import csv
import glob
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Union, Any

import easyocr
import re

from sympy import false

from definitions import ITEMS_PATH, CACHE_PATH, ROOT
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


class ScraperPriceCleaner:

    def __init__(self, scanner_boxes: MarketPlaceScannerBoxes):
        self.scanner_boxes = scanner_boxes

    def clean_price(self, prices: Union[None, list], file: str) -> list[PricePartModel]:  #TODO THIS IS ONLY FOR RESOURCES
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
            clean_price = price_value.replace('o', '0').replace('O', '0').replace(',', '').replace(' ','')
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
        tolerance = 4

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
        pack_price = self.price_cleaner.clean_price(prices, file)
        pack_price.insert(0, average_price)
        item_prices = []
        file = file[file.find('cache'):].replace('\\', '/').replace('//', '/')

        if file.count('/') != 4:
            raise Exception(f'File has more folders than expected: {file}')

        parts_creation_date = file.split('/')
        date_str = parts_creation_date[2]
        time_str = parts_creation_date[3]
        creation_date = datetime.strptime(date_str + time_str, '%Y%m%d%H%M%S')
        i = 1
        for price_part_model in pack_price:
            price_model = self.map(creation_date, file, price_part_model.price_type, name, price_part_model.price, i)
            item_prices.append(price_model)
            i = i + 1

        return item_prices

    def map(self, creation_date: datetime, file: str, price_type, name: str, price, auction_number: int) -> DofusPriceModel:
        price_model = DofusPriceModel()
        price_model.name = name.replace('WV', 'W')

        price_type_cleaned = str(price_type).replace(',', '').replace('x', '').replace('X', '').replace('o', '0').replace('O', '0').strip()
        if price_type_cleaned == '' or price_type_cleaned is None:
            price_type_cleaned = 1
        price_model.price_type = price_type_cleaned
        price_model.price = price
        price_model.auction_number = auction_number
        price_model.image_file_path = file
        price_model.creation_date = creation_date
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

    def get_sales(self, date: Union[None, datetime] = None, reimport: bool = False) -> list:
        if date is None:
            date = datetime.now()

        date = date.strftime("%Y%m%d")
        path = f"{ITEMS_PATH}/{date}/**/*.png"
        if reimport:
            path = f"{ITEMS_PATH}/**/*.png"
        list_of_files = glob.glob(path, recursive=True)
        count = len(list_of_files)

        i = 0
        for file in list_of_files:
            result = self.reader.readtext(file, detail=1, batch_size=5, blocklist='*#')
            if result is None or len(result) == 0:
                continue

            converted_result = self.convert(result)
            scraped_results = self.scrape.scrape(converted_result, file)

            for scraped_result in scraped_results:
                self.repo.insert(scraped_result)
            # self.write_to_file(scraped_result)
            i = i + 1
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Inserted {i} of {count} - {file}")

    def get_sale(self, file: str):
        path = ROOT + file
        result = self.reader.readtext(path, detail=1, batch_size=5, blocklist='*#')
        converted_result = self.convert(result)
        scraped_result = self.scrape.scrape(converted_result, path)

        print(scraped_result)

    #  def write_to_file(self, products: list):
    #      path = CACHE_PATH
    #      with open(f"{path}/products.csv", mode="a", newline="", encoding="utf-8") as file:
    #          writer = csv.writer(file, delimiter=';')
    #
    #          # If file is empty, write header first
    #          if file.tell() == 0:
    #              writer.writerow(["name", "price", "price_type","image_file_path","creation_date"])
    #
    #          # Write rows
    #          try:
    #              for product in products:
    #                  writer.writerow([product.name, product.price, product.price_type,product.file_name,product.creation_date])
    #          except Exception as e:
    #              print(e)

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
