import csv
import glob
from datetime import datetime, timezone
from typing import Union

import easyocr
import re

from definitions import ITEMS_PATH, CACHE_PATH
from repository.mysql import DofusPriceModel, ExternalDofusPriceRepository


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
        file = file[file.find('cache'):].replace('\\','/').replace('//','/')

        if file.count('/') != 4:
            raise Exception(f'File has more folders than expected: {file}')

        parts_creation_date = file.split('/')
        date_str = parts_creation_date[2]
        time_str = parts_creation_date[3]
        creation_date = datetime.strptime(date_str + time_str, '%Y%m%d%H%M%S')
        for key, price in pack_price.items(): #TODO NOT FOR SALE?
            price_model = self.map(creation_date, file, key, name, price)
            item_prices.append(price_model)

        price_model = self.map(creation_date, file, 'average', name, average_price)
        item_prices.append(price_model)

        return item_prices

    def map(self, creation_date: datetime, file: str, price_type, name: str, price) -> DofusPriceModel:
        price_model = DofusPriceModel()
        price_model.name = name.replace('WV', 'W')
        price_model.price_type = str(price_type).replace(',', '')
        price_model.price = price
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


    def clean_average_price(self, average_price: dict) -> int:
        is_number, number = self.find_number_with_comma(average_price['value'])

        return number

    def clean_price(self, prices: list) -> dict: #TODO THIS IS ONLY FOR RESOURCES
        product_prices = []
        pack = []
        if prices is None:
            return {}

        for price in prices:
            if price['value'] in ['Pack','Price']:
                continue

            price['value'] =  price['value'].replace('o', '0')
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
        self.repo = ExternalDofusPriceRepository()

    def get_sales(self, date: Union[None,datetime] = None) -> list:
        if date is None:
            date = datetime.now()

        date = date.strftime("%Y%m%d")

        path = f"{ITEMS_PATH}/{date}/**/*.png"
        list_of_files = glob.glob(path, recursive=True)

        for file in list_of_files:
            result = self.reader.readtext(file, detail=1, batch_size=5, blocklist='*#')
            if result is None or len(result) == 0:
                continue

            converted_result = self.convert(result)
            scraped_results = self.scrape.scrape(converted_result, file)

            for scraped_result in scraped_results:
                self.repo.insert(scraped_result)
           # self.write_to_file(scraped_result)

    def get_sale(self,file : str):

        result = self.reader.readtext(file, detail=1, batch_size=5, blocklist='*#')
        converted_result = self.convert(result)
        scraped_result = self.scrape.scrape(converted_result, file)
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


