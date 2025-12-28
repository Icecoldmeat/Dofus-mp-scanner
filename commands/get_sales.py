from datetime import datetime

from marketplace_boxes import large_text_box
from scraper import ScraperManager, Scraper

manager = ScraperManager(Scraper(large_text_box))
#manager.get_sale('\\cache\\items\\20251227\\143247\\70.png')
#manager.get_sale('\\cache\items\\20251227\\163020\\2.png')
#manager.get_sale('\\cache\\items\\20251228\\122736\\0.png')
date = datetime(year=2025,month=12,day=27)
manager.get_sales(date)

#C:\Users\richa\Documents\Python\Dofus-mp-scanner\cache\items\20251228\122736
#C:\Users\richa\Documents\Python\Dofus-mp-scanner/cache//items/20251227\143247\70.png