from marketplace_boxes import average_text_box
from repository.mysql import ExternalDofusPriceRepository
from scraper import ScraperManager, SubjectScraper

stuff = [
    # '/cache/items/processed/20260103/113231/64.png',
    '/cache//items/unprocessed\\20251222\\114557\\104.png'
]
manager = ScraperManager(SubjectScraper(average_text_box))

for stuf in stuff:
    scraped_sales = manager.get_sale(stuf)
    repo = ExternalDofusPriceRepository()
    for sale in scraped_sales:
        sale.image_file_path = sale.image_file_path.replace('processed', 'unprocessed')
#     repo.upsert(sale)


# date = datetime(year=2025,month=12,day=31)
# C:\Users\richa\Documents\Python\Dofus-mp-scanner\cache\items\20251228\122736
# C:\Users\richa\Documents\Python\Dofus-mp-scanner/cache//items/20251227\143247\70.png
# C:\Users\richa\Documents\Python\Dofus-mp-scanner/cache//items/20251231\173240\175.png
