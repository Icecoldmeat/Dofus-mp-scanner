import pandas as pd
from sqlalchemy import create_engine

from connect import SqlAlchemyConnector
from repository.mongodb import DofusPricesRepository, DofusItemRepository

df_prices = DofusPricesRepository().find_all_items()
df_prices = pd.DataFrame(df_prices)
df_prices = df_prices.sort_values(by=['creation_date'])
df_prices = df_prices.drop_duplicates(subset=["item_id", "price_type"],keep="last")  #TODO

df_prices = df_prices[df_prices['price_type'].isin(['1', '10', '100', '1000'])]
df_prices = df_prices.astype({'price_type': 'int'})
df_prices['unit_price'] = df_prices['price'] / df_prices['price_type']

df_items = DofusItemRepository().find_all_items(DofusItemRepository().PROJECTION_NUGGETS)
df_items = pd.DataFrame(df_items)
df_items = df_items[df_items['recyclingNuggets'] > 0]


joined = df_prices.join(df_items.set_index('item_id'), on='item_id')
joined['nuggetPrice'] = 350
joined['price_one_nugget'] = joined['unit_price'] / joined['recyclingNuggets']
joined['profitable_until_unit_price'] = joined['nuggetPrice'] / (1/joined['recyclingNuggets']) * 1.02
joined['profit'] = joined['price_type'] * joined['recyclingNuggets'] * joined['nuggetPrice'] - joined['price']
df_prices = df_prices.astype({'price_type': 'int'})

joined["creation_date"] = pd.to_datetime(joined["creation_date"])

engine = SqlAlchemyConnector().connect('postgresql')
joined.to_sql('profitable_nuggets_tb', engine, if_exists="replace")

#select concat(name, ' - ',price_type, ' lot - ', unit_price , ' kamas') as name_price, ("price_type" * "recyclingNuggets" * "nuggetPrice") - "price" as profit from profitable_nuggets_tb where "nuggetPrice" > price_one_nugget order by price_one_nugget asc
