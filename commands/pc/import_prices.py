import pandas as pd
from definitions import PRICES_PATH
from repository.mongodb import DofusItemRepository, DofusPricesRepository
from repository.mysql import ExternalDofusPriceRepository
from transformations.dofus_prices import PriceTransformation

path = PRICES_PATH

#TODO create a script that can signal if names are equal but item_id is not


item_list = DofusItemRepository().find_all_items()

df_items = pd.DataFrame(item_list)
df_items = df_items.drop_duplicates(subset=["name"], keep="last")

df_prices = ExternalDofusPriceRepository().find_all()
df_prices = df_prices.drop_duplicates(subset=["price_type", "image_file_path"])
joined = df_prices.join(df_items.set_index('name'), on='name')

df = joined.apply(PriceTransformation().find_closest_match, axis=1)

price_repository = DofusPricesRepository()

last_id = -1
entity_last_id = price_repository.find_last_id()
if len(entity_last_id) != 0:
    last_id = entity_last_id[0]['id']

df = df[df["id"] > last_id]


df_reordered = df.loc[:, ['id', 'item_id', 'name', 'corrupt_name', 'price_type', 'price', 'image_file_path',  'creation_date']]
price_repository.add_dataframe(df_reordered)

print('hello')


