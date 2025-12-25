from datetime import datetime, timedelta, UTC
import os

import pandas as pd
from pymongo import ASCENDING
from pymongo.synchronous.collection import Collection
from pymongo import errors
from src.connect import MongoConnector


class DofusRepository:

    def __init__(self, table_name: str):
        client = MongoConnector(os.environ.get("MONGO_CONNECTION_STRING")).connect()
        self.db = client['dofus']
        self.collection: Collection
        self.table_name = table_name
        self.collection = self.db[table_name]

    def add_multiple(self, values: list[dict]) -> None:
        ids_to_check = []
        for value in values:
            ids_to_check.append(value['m_id'])

        existing_documents = self.collection.find({"m_id": {"$in": ids_to_check}}, {"m_id": 1, "_id": 0})
        existing_ids = {doc['m_id'] for doc in existing_documents}
        unique_documents = [v for v in values if v['m_id'] not in existing_ids]
        if len(unique_documents) > 0:
            self.collection.insert_many(unique_documents)

    def add_dataframe(self, df: pd.DataFrame) -> None:
        self.collection.insert_many(df.to_dict('records'))


class DofusItemRepository(DofusRepository):
    PROJECTION_DEFAULT = {
        "_id": 0,  # exclude MongoDB's default _id
        "item_id": "$m_id",
        "name": "$name.en"
    }

    PROJECTION_NUGGETS = {
        "_id": 0,
        "item_id": "$m_id",
        "recyclingNuggets": "$recyclingNuggets"
    }

    def __init__(self):
        super().__init__('item')

    def find_all_items(self, projection: dict = None):
        if projection is None:
            projection = self.PROJECTION_DEFAULT

        results = self.collection.find({}, projection)

        return list(results)

    def find_by_name_part(self, name_part: str):
        query = {
            "$and": [
                {"name.en": {"$regex": f"^{name_part}"}},
                {"exchangeable": True}
            ]
        }

        results = self.collection.find(query, self.PROJECTION)

        return list(results)


class DofusRecipeRepository(DofusRepository):

    def __init__(self):
        super().__init__('recipe')

    def find_by_repository_name(self):
        projection = {
            "_id": 0,  # exclude MongoDB's default _id
            "level": 1,
            "id": "$m_id",
            "name": "$name.en"
        }

        results = self.collection.find({}, projection)

        return list(results)


class DofusPricesRepository(DofusRepository):
    PROJECTION_DEFAULT = {
        "_id": 0,
        "name": "$name",
        "item_id": "$item_id",
        "price_type": "$price_type",
        "price": "$price",
        "creation_date": "$creation_date",

    }


    def __init__(self):
        super().__init__('price')
        self.collection.create_index(
            [
                ("image_file_path", ASCENDING),
                ("price_type", ASCENDING),
            ],
            unique=True,
            name="uniq_file_path_price_type"
        )

    def find_last_id(self):
        results = self.collection.find({}).sort({"id": -1}).limit(1)

        return list(results)

    def find_all_items(self, projection: dict = None):
        if projection is None:
            projection = self.PROJECTION_DEFAULT

        results = self.collection.find({}, projection)

        return list(results)
