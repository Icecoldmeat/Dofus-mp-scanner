import glob
import time
from datetime import datetime

import cv2

from definitions import UNPROCESSED_ITEMS_PATH, ROOT
from marketplace_boxes import average_text_box
from repository.mysql import ExternalDofusPriceRepository
from scraper import ScraperManager, Scraper

manager = ScraperManager(Scraper(average_text_box))


def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)
    return thresh

path = '/cache/items/processed/20260101/123439/28.png'
path_root = f"{ROOT}{path}"
img = cv2.imread(path_root)
if img is None:
    raise ValueError("Image not found")

h, w = img.shape[:2]

img = preprocess(img)

cv2.imshow('image',img)
cv2.waitKey(0)


scraped_sales = manager.get_sale('/cache/items/processed/20260101/123439/28.png')

#date = datetime(year=2025,month=12,day=31)
#C:\Users\richa\Documents\Python\Dofus-mp-scanner\cache\items\20251228\122736
#C:\Users\richa\Documents\Python\Dofus-mp-scanner/cache//items/20251227\143247\70.png
#C:\Users\richa\Documents\Python\Dofus-mp-scanner/cache//items/20251231\173240\175.png