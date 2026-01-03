import os
import sys
import unittest

from definitions import ROOT
from marketplace_boxes import average_text_box
from repository.mysql import DofusPriceModel
from scraper import ScraperManager, Scraper


class SalesTest(unittest.TestCase):
    def test(self):
        manager = ScraperManager(Scraper(average_text_box))

        images_to_test = self.get_images_to_test()
        all_expected_sales = self.get_sales()

        for image in images_to_test:
            file_name = os.path.basename(image)
            expected_sales = all_expected_sales[file_name]
            actual_sales = manager.get_sale(image)

            # Subtest per image
            with self.subTest(image=file_name):
                for i, actual_sale in enumerate(actual_sales):
                    with self.subTest(sale_index=i):
                        self.assertEqual(expected_sales[i].name, actual_sale.name, f"{expected_sales[i].name}")
                        self.assertEqual(expected_sales[i].price, actual_sale.price, f"{expected_sales[i].name}")
                        self.assertEqual(expected_sales[i].auction_number, actual_sale.auction_number)
                        self.assertEqual(expected_sales[i].price_type, actual_sale.price_type)


    def get_images_to_test(self) -> list:
        path = '/test/images/cache/20251227/130828/'

        file_names = ['belteen.png',
                      'castus_flower.png',
                      'fish_juice.png',
                      'ice_knight_map.png',
                      'rhinteele_ring.png', ]
        file_path = []
        for file_name in file_names:
            file_path.append(f'{path}{file_name}')

        return file_path

    def get_sales(self) -> dict[list[DofusPriceModel]]:

        return {
            'belteen.png': [
                DofusPriceModel(name='Belteen', price=5636427.0, auction_number=1, price_type='average'),
                DofusPriceModel(name='Belteen', price=5990000.0, auction_number=2, price_type='1'),
                DofusPriceModel(name='Belteen', price=5999999.0, auction_number=3, price_type='1'),
                DofusPriceModel(name='Belteen', price=600000.0, auction_number=4, price_type='1'),
                DofusPriceModel(name='Belteen', price=6250000.0, auction_number=5, price_type='1'),
            ],
            'castus_flower.png': [
                DofusPriceModel(name='Castupod Flower', price=163.0, auction_number=1, price_type='average'),
                DofusPriceModel(name='Castupod Flower', price=200.0, auction_number=2, price_type='1'),
                DofusPriceModel(name='Castupod Flower', price=2100.0, auction_number=3, price_type='10'),
                DofusPriceModel(name='Castupod Flower', price=20994.0, auction_number=4, price_type='100'),
            ],
            'fish_juice.png': [
                DofusPriceModel(name='Asphyxiating Fish Juice', price=1933955.0, auction_number=1,price_type='average'),
                DofusPriceModel(name='Asphyxiating Fish Juice', price=2798998.0, auction_number=2, price_type='1'),
            ],
            'ice_knight_map.png': [
                DofusPriceModel(name="Ice Knight' $ Map", price=2369776.0, auction_number=1, price_type='average'),
                DofusPriceModel(name="Ice Knight' $ Map", price=1799980.0, auction_number=2, price_type='1'),
            ],
            'rhinteele_ring.png': [
                DofusPriceModel(name='Rhineetle Ring', price=6649082.0, auction_number=1, price_type='average'),
                DofusPriceModel(name='Rhineetle Ring', price=6000000.0, auction_number=2, price_type='1'),
                DofusPriceModel(name='Rhineetle Ring', price=7000000.0, auction_number=3, price_type='1'),
                DofusPriceModel(name='Rhineetle Ring', price=7099999.0, auction_number=4, price_type='1'),
                DofusPriceModel(name='Rhineetle Ring', price=7499999.0, auction_number=5, price_type='1'),
            ]

        }
