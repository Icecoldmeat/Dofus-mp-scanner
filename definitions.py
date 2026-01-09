import os

# paths

ROOT = os.path.dirname(os.path.realpath(__file__))
DOTENV_PATH = ROOT + "/.env"
SOURCE_PATH = ROOT + "/src/"
CACHE_PATH = ROOT + "/cache/"
IMAGE_PATH = ROOT + "/images/"
UNPROCESSED_ITEMS_PATH = CACHE_PATH + "/items/unprocessed"
PROCESSED_ITEMS_PATH = CACHE_PATH + "/items/processed"
PRICES_PATH = CACHE_PATH + "/prices"
