import glob
import time
from datetime import datetime

from definitions import UNPROCESSED_ITEMS_PATH
from marketplace_boxes import average_text_box
from repository.mysql import ExternalDofusPriceRepository
from scraper import ScraperManager, Scraper

manager = ScraperManager(Scraper(average_text_box))


#manager.get_sale('\\cache\\items\\20251228\\170431\\100.png')
#manager.get_sale('\\cache\items\\20251227\\163020\\2.png')
#manager.get_sale('\\cache//items/20251231\\173240\\176.png')
#date = datetime(year=2025,month=12,day=31)
while True:
    path = f"{UNPROCESSED_ITEMS_PATH}/**/*.png"
    list_of_files = glob.glob(path, recursive=True)
    count = len(list_of_files)

    if count > 0:
        manager.get_sales()

    print("No items found, sleeping for 5 seconds...")
    time.sleep(5)

#C:\Users\richa\Documents\Python\Dofus-mp-scanner\cache\items\20251228\122736
#C:\Users\richa\Documents\Python\Dofus-mp-scanner/cache//items/20251227\143247\70.png
#C:\Users\richa\Documents\Python\Dofus-mp-scanner/cache//items/20251231\173240\175.png