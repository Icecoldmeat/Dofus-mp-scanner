import glob
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from time import sleep
from typing import Union, Any

import cv2
import easyocr
import numpy as np

from definitions import UNPROCESSED_ITEMS_PATH, ROOT
from marketplace_boxes import MarketPlaceScannerBoxes
from repository.mysql import DofusPriceModel, ExternalDofusPriceRepository


@dataclass
class PricePartModel:
    price: int
    price_type: str  # average or lot
    quantity: int


@dataclass
class DirtyOffers:
    name: Union[str, None]
    average_price: Union[str, None]
    pack: Union[list[dict], None]
    price: Union[list[dict], None]


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

        return groups  # not in use


class SubjectScraper:

    def __init__(self, scanner_boxes: MarketPlaceScannerBoxes):
        self.scanner_boxes = scanner_boxes
        self.reader = easyocr.Reader(['en'], gpu=True)

    def scrape(self, image: np.ndarray) -> Union[None, DirtyOffers]:
        name = self._scrape_name(image)

        if name is None:
            return None

        # TODO not for sale

        average_price = self._scrape_average_price(image)
        pack = self._scrape_pack(image)
        price = self._scrape_price(image)

        return DirtyOffers(
            name=name,
            average_price=average_price,
            pack=pack,
            price=price,
        )

    def _scrape_name(self, image: np.ndarray):
        name_crop = image[self.scanner_boxes.mp_item_page_name_crop]
        names = self._ocr_with_allowlist(name_crop, {
            'allowlist': '/ abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ 123456789 ''',
            'batch_size': 50,
            'slope_ths': 0.4,
            'width_ths': 1,
            'height_ths': 1})

        if len(names) == 0:
            return None

        names = self._convert(names)
        if len(names) == 1:
            return names[0]['value']

        sorted_data = sorted(names, key=lambda d: d['x'])

        return " ".join(v["value"] for v in sorted_data)

    def _scrape_average_price(self, image: np.ndarray):
        avg_price_crop = image[self.scanner_boxes.mp_item_page_average_price_crop]
        average_price = self._ocr_with_allowlist(avg_price_crop, {
            'allowlist': 'AP average price 0123456789, K',
            'batch_size': 50,
            'slope_ths': 0.4,
            'width_ths': 1})

        if len(average_price) == 0:
            return None

        average_price = self._convert(average_price)
        if len(average_price) == 1:
            return average_price[0]['value']

        sorted_data = sorted(average_price, key=lambda d: d['x'])

        return " ".join(v["value"] for v in sorted_data)

    def _scrape_pack(self, image: np.ndarray) -> Union[None, list]:
        pack_crop = image[self.scanner_boxes.mp_item_page_pack_crop]
        pack = self._ocr_with_allowlist(pack_crop, {
            'allowlist': 'P pack x1 x10 x100 x1000',
            'batch_size': 50,
            'low_text': 0.1})

        if len(pack) == 0:
            return None

        pack = self._convert(pack)

        return pack

    def _scrape_price(self, image: np.ndarray) -> Union[None, list]:
        price_crop = image[self.scanner_boxes.mp_item_page_price_crop]
        price = self._ocr_with_allowlist(price_crop, {
            'allowlist': 'P price 0123456789, K',
            'batch_size': 50,
            'low_text': 0.2,
            'ycenter_ths': 0.75,
            'slope_ths': 0.4,
            'height_ths': 1})

        price = self._convert(price)

        return price

    def _ocr_with_allowlist(self, img_to_ocr: np.ndarray, arguments: dict):
        rgb = cv2.cvtColor(img_to_ocr, cv2.COLOR_BGR2RGB)
        results = self.reader.readtext(rgb, **arguments)

        return results

    def _convert(self, result: list) -> list:
        all_values = []
        for item in result:
            values = {
                'value': item[1],
                'x': int(item[0][0][0]),
                'y': int(item[0][0][1]),
            }
            all_values.append(values)

        return all_values

    def _concat_items(self, value_list: list[Any]):
        concat_values = []
        for value in value_list:
            result = {
                'value': ''.join(item['value'] for item in value_list),
                'x': value[0]['x'],
                'y': value[0]['y']
            }

            concat_values.append(result)

        return concat_values


class SubjectCleaner:

    def clean(self, dirty_offers: DirtyOffers, file: str) -> list[DofusPriceModel]:

        if dirty_offers is None or dirty_offers.name is None:
            return []

        file = file[file.find('cache'):].replace('\\', '/').replace('//', '/')
        creation_date = ScraperUtility.folder_path_to_creation_date(file)

        name = self._clean_name(dirty_offers.name)
        average_price = self._clean_average_price(dirty_offers.average_price)
        packs = self._clean_pack(dirty_offers.pack)
        prices = self._clean_price(dirty_offers.price)
        price_part_models = self._merge_price_pack(packs, prices)
        price_part_models.insert(0, average_price)

        i = 1
        dofus_price_models = []
        for price_part_model in price_part_models:
            price_model = self._map(
                file=file,
                creation_date=creation_date,
                name=name,
                price_type=price_part_model.price_type,
                price=price_part_model.price,
                quantity=price_part_model.quantity,
                auction_number=i,
            )
            dofus_price_models.append(price_model)
            i = i + 1

        return dofus_price_models

    def _clean_name(self, name: str) -> str:
        return name.replace('WV', 'W')

    def _clean_average_price(self, average_price: str) -> PricePartModel:
        if average_price is None:
            raise Exception('Average price should not be None')

        average_price = average_price.replace(' ', '').replace(',', '').replace('.', '')

        is_number, number = ScraperUtility.find_number_with_comma(average_price)

        return PricePartModel(int(number), 'average', 1)

    def _clean_pack(self, packs: Union[None, list[dict]]) -> list:
        if packs is None or len(packs) == 0:
            return []

        if packs[0]['value'].count('i') > 1:
            return []  # not for sale, but lots of letters are blacklisted resulting in lots of i's

        grouped_packs = self._group_prices_by_y(packs)
        for grouped_pack in grouped_packs:
            if len(grouped_pack) > 1:
                raise Exception('More than one pack in line, probably need to concat, gief example')

        cleaned_packs = []
        for pack_list in packs:
            pack = pack_list['value']
            pack = pack.replace(' ', '').replace(',', '').replace('.', '').replace('x', '')
            is_number, number = ScraperUtility.find_number_with_comma(pack)

            if is_number:
                cleaned_packs.append(int(number))

        return cleaned_packs

    def _clean_price(self, prices: Union[None, list[dict]]) -> list:
        if len(prices) == 0 or prices is None:
            return []

        if prices[0]['value'].count('i') > 1:
            return []  # not for sale, but lots of letters are blacklisted resulting in lots of i's

        grouped_prices = self._group_prices_by_y(prices)
        for grouped_price in grouped_prices:
            if len(grouped_price) > 1:
                raise Exception('More than one price in line, probably need to concat, gief example')

        cleaned_prices = []
        for price_list in prices:
            price = price_list['value']
            price = (price
                     .replace('o', '0')
                     .replace('O', '0')
                     .replace(' ', '')
                     .replace('.', '')
                     .replace('x', '')
                     .replace('K', '')
                     .replace('k', ''))

            if ',' in price[-3:]:
                raise Exception(f'price should not contain comma: {price}')

            price = price.replace(',', '')
            is_number, number = ScraperUtility.find_number_with_comma(price)

            if is_number:
                cleaned_prices.append(int(number))

        return cleaned_prices

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

    def _merge_price_pack(self, pack: list[Any], product_prices: list[Any]) -> list[PricePartModel]:
        if len(pack) != len(product_prices):
            packs = [1, 10, 100, 1000]
            if pack.count(1) > 1 and pack.count(10) == 0 and pack.count(100) == 0 and pack.count(1000) == 0:
                packs = [1, 1, 1, 1]

            pack = packs[:len(product_prices)]

            if len(product_prices) > 4:
                raise Exception('product_prices cant be this high')

        price_part_models = [PricePartModel(a, 'lot', b) for a, b in zip(product_prices, pack)]

        return price_part_models

    def _map(self,
             file: str,
             creation_date: datetime,
             price_type,
             name: str,
             price: int,
             auction_number: int,
             quantity: int
             ) -> DofusPriceModel:
        price_model = DofusPriceModel()
        price_model.name = name
        price_model.price_type = price_type
        price_model.price = price
        price_model.quantity = quantity
        price_model.auction_number = auction_number
        price_model.image_file_path = file
        price_model.creation_date = creation_date
        price_model.update_date = creation_date
        return price_model


class ScraperManager:

    def __init__(self, scraper: SubjectScraper) -> None:
        self.reader = easyocr.Reader(['en'], gpu=True)
        self.scrape = scraper
        self.cleaner = SubjectCleaner()
        self.repo = ExternalDofusPriceRepository()

    def get_sales(self) -> None:
        path = f"{UNPROCESSED_ITEMS_PATH}/**/*.png"
        list_of_files = glob.glob(path, recursive=True)
        count = len(list_of_files)

        sleep(2)  # make sure images are saved
        i = 0
        for file in list_of_files:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Processing {i} of {count} - {file}")
            image = self.preprocess(file)
            scraped_results = self.scrape.scrape(image)
            scraped_results = self.cleaner.clean(scraped_results, file)

            for scraped_result in scraped_results:
                self.repo.insert(scraped_result)
            self.move_file_to_processed(file)

            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Inserted {i} of {count} - {file}")
            i = i + 1

    def get_sale(self, file: str) -> Union[None, list[DofusPriceModel]]:
        path = ROOT + file
        image = self.preprocess(path)

        scraped_results = self.scrape.scrape(image)
        scraped_result = self.cleaner.clean(scraped_results, file)
        return scraped_result

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
