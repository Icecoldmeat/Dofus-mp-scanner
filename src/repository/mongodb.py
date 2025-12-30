from datetime import datetime, timedelta, UTC
import os

import pandas as pd
from pymongo import ASCENDING
from pymongo.synchronous.collection import Collection
from pymongo import errors
from src.connect import MongoConnector


class DofusRepository:

    def __init__(self, table_name: str):
        client = MongoConnector().connect()
        self.db = client['dofus']
        self.collection: Collection
        self.table_name = table_name
        self.collection = self.db[table_name]

    def find_all_items(self, projection: dict = None) -> pd.DataFrame:

        results = self.collection.find({}, projection)

        return pd.DataFrame(list(results))

    def find_all_items_as_list(self, projection: dict = None) -> list:

        results = self.collection.find({}, projection)

        return list(results)

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

    PROJECTION_RECIPES = {
        "_id": 0,
        "item_id": "$m_id",
        "item_type": "$type.name.en",
    }

    PROJECTION_CRUSH = {
        "_id": 0,
        "name": "$name.en",
        "item_id": "$m_id",
        "item_type": "$type.name.en",
        "effects": "$effects",
    }

    def __init__(self):
        super().__init__('item')

    def find_by_name_part(self, name_part: str):
        escaped_name_part = name_part.replace('(', '').replace(')', '').strip()
        query = {
            "$and": [
                {"name.en": {"$regex": f"^{escaped_name_part}"}},
                {"exchangeable": True}
            ]
        }

        results = self.collection.find(query, self.PROJECTION_DEFAULT)

        return list(results)


class DofusRecipeRepository(DofusRepository):
    PROJECTION_DEFAULT = {
        "_id": 0,
        "name": "$resultName.en",
        "item_id": "$resultId",
        #    "item_type": "$resultType.name.en",
        "ingredient_quantities": "$quantities",
        "ingredients": "$ingredients",
        "job": "$job.name.en",
        "job_level": "$resultLevel",
    }

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
                ("auction_number", ASCENDING),
            ],
            unique=True,
            name="uniq_file_path_price_type"
        )

    def find_last_id(self):
        results = self.collection.find({}).sort({"id": -1}).limit(1)

        return list(results)


class DofusEffectsRepository(DofusRepository):
    PROJECTION_DEFAULT = {
        "_id": 0,
        "id": "$id",
        "density": "$effectPowerRate",
    }

    def __init__(self):
        super().__init__('effect')

    def find_last_id(self):
        results = self.collection.find({}).sort({"id": -1}).limit(1)

        return list(results)


class DofusCharacteristicRepository(DofusRepository):
    PROJECTION_DEFAULT = {
        "_id": 0,
        "id": "$id",
        "characteristic": "$name.en",
    }

    def __init__(self):
        super().__init__('characteristic')

    def find_last_id(self):
        results = self.collection.find({}).sort({"id": -1}).limit(1)

        return list(results)
