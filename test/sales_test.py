import os
import unittest

from marketplace_boxes import average_text_box
from repository.mysql import DofusPriceModel
from scraper import ScraperManager, SubjectScraper


class SalesTest(unittest.TestCase):
    def test(self):
        manager = ScraperManager(SubjectScraper(average_text_box))

        images_to_test = self.get_images_to_test()
        all_expected_sales = self.get_sales()

        for image in images_to_test:
            file_name = os.path.basename(image)

            actual_sales = manager.get_sale(image)

            for actual_sale in actual_sales:
                print(
                    f"name='{actual_sale.name}', price={actual_sale.price}, auction_number={actual_sale.auction_number}, price_type='{actual_sale.price_type}', quantity={actual_sale.quantity}")

            expected_sales = all_expected_sales[file_name]
            # Subtest per image
            with self.subTest(image=file_name):
                for i, actual_sale in enumerate(actual_sales):
                    with self.subTest(sale_index=i):
                        self.assertEqual(actual_sale.name, expected_sales[i].name,
                                         f"{expected_sales[i].name} actual vs expected")
                        self.assertEqual(actual_sale.price, expected_sales[i].price,
                                         f"{expected_sales[i].name} actual vs expected")
                        self.assertEqual(actual_sale.auction_number, expected_sales[i].auction_number,
                                         f"{expected_sales[i].name} actual vs expected")
                        self.assertEqual(actual_sale.price_type, expected_sales[i].price_type,
                                         f"{expected_sales[i].name} actual vs expected")
                        self.assertEqual(actual_sale.quantity, expected_sales[i].quantity,
                                         f"{expected_sales[i].quantity} actual vs expected")

    def get_images_to_test(self) -> list:
        path = '/test/images/cache/20251227/130828/'
        file_names = ['ra_fire_res.png',
                      'fragment.png',
                      'mantax.png',
                      'cheeken.png',
                      'belteen.png',
                      'castus_flower.png',
                      'fish_juice.png',
                      'ice_knight_map.png',
                      'rhinteele_ring.png',
                      'bone_band.png',
                      'akakwa_pants.png',
                      'brakmar_shield.png',
                      'bulwark.png',
                      'captain_chafter_briefs.png',
                      'goul_shield.png',
                      ]
        file_path = []
        for file_name in file_names:
            file_path.append(f'{path}{file_name}')

        return file_path

    def get_sales(self) -> dict[list[DofusPriceModel]]:
        # @formatter:off
        return {
            'ra_fire_res.png': [
                DofusPriceModel(name='Ra Fire Res Rune', price=1534, auction_number=1, price_type='average', quantity=1),
                DofusPriceModel(name='Ra Fire Res Rune', price=888, auction_number=2, price_type='lot', quantity=1),
                DofusPriceModel(name='Ra Fire Res Rune', price=11986, auction_number=3, price_type='lot', quantity=10),
                DofusPriceModel(name='Ra Fire Res Rune', price=169991, auction_number=4, price_type='lot', quantity=100),
                DofusPriceModel(name='Ra Fire Res Rune', price=1235412, auction_number=5, price_type='lot', quantity=1000),
            ],
            'fragment.png': [
                DofusPriceModel(name='Anomaly Fragment', price=5086, auction_number=1, price_type='average', quantity=1),
                DofusPriceModel(name='Anomaly Fragment', price=5810, auction_number=2, price_type='lot', quantity=1),
                DofusPriceModel(name='Anomaly Fragment', price=49510, auction_number=3, price_type='lot', quantity=10),
                DofusPriceModel(name='Anomaly Fragment', price=518994, auction_number=4, price_type='lot', quantity=100),
            ],
            'goul_shield.png': [
                DofusPriceModel(name='Goulshield', price=2908224, auction_number=1, price_type='average', quantity=1),
                DofusPriceModel(name='Goulshield', price=2699999, auction_number=2, price_type='lot', quantity=1),
                DofusPriceModel(name='Goulshield', price=2800000, auction_number=3, price_type='lot', quantity=1),
                DofusPriceModel(name='Goulshield', price=3000000, auction_number=4, price_type='lot', quantity=1),
                DofusPriceModel(name='Goulshield', price=3600000, auction_number=5, price_type='lot', quantity=1),
                 ],
            'captain_chafter_briefs.png': [
                DofusPriceModel(name='Captain Chafer s Briefs', price=6864614, auction_number=1, price_type='average', quantity=1),
                DofusPriceModel(name='Captain Chafer s Briefs', price=5500000, auction_number=2, price_type='lot', quantity=1),
                DofusPriceModel(name='Captain Chafer s Briefs', price=6300000, auction_number=3, price_type='lot', quantity=1),
                DofusPriceModel(name='Captain Chafer s Briefs', price=6777770, auction_number=4, price_type='lot', quantity=1),
            ],
            'bulwark.png': [
                DofusPriceModel(name='Major Water Bulwark', price=901117, auction_number=1, price_type='average', quantity=1)
            ],
            'brakmar_shield.png': [
                DofusPriceModel(name='Brakmarian Shield', price=1953908, auction_number=1, price_type='average', quantity=1),
                DofusPriceModel(name='Brakmarian Shield', price=3500000, auction_number=2, price_type='lot', quantity=1),
                DofusPriceModel(name='Brakmarian Shield', price=4899999, auction_number=3, price_type='lot', quantity=1),
                DofusPriceModel(name='Brakmarian Shield', price=5000123, auction_number=4, price_type='lot', quantity=1),
                DofusPriceModel(name='Brakmarian Shield', price=6500123, auction_number=5, price_type='lot', quantity=1),
            ],
            'bone_band.png': [
                DofusPriceModel(name='Bone Band', price=50613, auction_number=1, price_type='average', quantity=1)
            ],
            'akakwa_pants.png': [
                DofusPriceModel(name='Akakwa Akapants', price=84, auction_number=1, price_type='average', quantity=1),
                DofusPriceModel(name='Akakwa Akapants', price=74, auction_number=2, price_type='lot', quantity=1),
                DofusPriceModel(name='Akakwa Akapants', price=879, auction_number=3, price_type='lot', quantity=10),
                DofusPriceModel(name='Akakwa Akapants', price=8999, auction_number=4, price_type='lot', quantity=100),
                DofusPriceModel(name='Akakwa Akapants', price=179999, auction_number=5, price_type='lot', quantity=1000),
            ],
            'mantax.png': [
                DofusPriceModel(name='Mantax', price=5465453, auction_number=1, price_type='average', quantity=1),
                DofusPriceModel(name='Mantax', price=6100000, auction_number=2, price_type='lot', quantity=1),
                DofusPriceModel(name='Mantax', price=6222222, auction_number=3, price_type='lot', quantity=1),
                DofusPriceModel(name='Mantax', price=6300000, auction_number=4, price_type='lot', quantity=1),
                DofusPriceModel(name='Mantax', price=6349999, auction_number=5, price_type='lot', quantity=1),
            ],
            'cheeken.png': [
                DofusPriceModel(name='Cheeken Cloaca', price=1978, auction_number=1, price_type='average', quantity=1),
                DofusPriceModel(name='Cheeken Cloaca', price=2392, auction_number=2, price_type='lot', quantity=1),
                DofusPriceModel(name='Cheeken Cloaca', price=19993, auction_number=3, price_type='lot', quantity=10),
                DofusPriceModel(name='Cheeken Cloaca', price=180000, auction_number=4, price_type='lot', quantity=100),
                DofusPriceModel(name='Cheeken Cloaca', price=2449996, auction_number=5, price_type='lot', quantity=1000),
            ],
            'belteen.png': [
                DofusPriceModel(name='Belteen', price=5636427, auction_number=1, price_type='average', quantity=1),
                DofusPriceModel(name='Belteen', price=5990000, auction_number=2, price_type='lot', quantity=1),
                DofusPriceModel(name='Belteen', price=5999999, auction_number=3, price_type='lot', quantity=1),
                DofusPriceModel(name='Belteen', price=6000000, auction_number=4, price_type='lot', quantity=1),
                DofusPriceModel(name='Belteen', price=6250000, auction_number=5, price_type='lot', quantity=1),
            ],
            'castus_flower.png': [
                DofusPriceModel(name='Castupod Flower', price=163, auction_number=1, price_type='average', quantity=1),
                DofusPriceModel(name='Castupod Flower', price=200, auction_number=2, price_type='lot', quantity=1),
                DofusPriceModel(name='Castupod Flower', price=2100, auction_number=3, price_type='lot', quantity=10),
                DofusPriceModel(name='Castupod Flower', price=20994, auction_number=4, price_type='lot', quantity=100),
            ],
            'fish_juice.png': [
                DofusPriceModel(name='Asphyxiating Fish Juice', price=1933955, auction_number=1,price_type='average', quantity=1),
                DofusPriceModel(name='Asphyxiating Fish Juice', price=2798998, auction_number=2, price_type='lot', quantity=1),
            ],
            'ice_knight_map.png': [
                DofusPriceModel(name="Ice Knight s Map", price=2369776, auction_number=1, price_type='average', quantity=1),
                DofusPriceModel(name="Ice Knight s Map", price=1799980, auction_number=2, price_type='lot', quantity=1),
            ],
            'rhinteele_ring.png': [
                DofusPriceModel(name='Rhineetle Ring', price=6649082, auction_number=1, price_type='average', quantity=1),
                DofusPriceModel(name='Rhineetle Ring', price=6000000, auction_number=2, price_type='lot', quantity=1),
                DofusPriceModel(name='Rhineetle Ring', price=7000000, auction_number=3, price_type='lot', quantity=1),
                DofusPriceModel(name='Rhineetle Ring', price=7099999, auction_number=4, price_type='lot', quantity=1),
                DofusPriceModel(name='Rhineetle Ring', price=7499999, auction_number=5, price_type='lot', quantity=1),
            ],

        }

    # @formatter:on
