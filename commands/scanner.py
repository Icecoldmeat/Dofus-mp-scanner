"""This code is executed before starting any other code"""
from marketplace import MarketScanner
from marketplace_boxes import average_text_box

mpscanner = MarketScanner(average_text_box)
mpscanner.startup()
mpscanner.retrieve_marketplace_images()
