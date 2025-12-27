from datetime import datetime

from scraper import ScraperManager

manager = ScraperManager()
#manager.get_sale('cache/items\\20251222\\215330\\0.png')
date = datetime(year=2025,month=12,day=22)
manager.get_sales()