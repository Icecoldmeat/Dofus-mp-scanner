from datetime import datetime, timedelta, UTC
import os
from pymongo.synchronous.collection import Collection

from src.connect import MongoConnector


class DofusRepository:
    TABLE_RECIPE = 'recipe'
    TABLE_ITEM = 'item'

    def __init__(self, table_name: str):
        client = MongoConnector(os.environ.get("MONGO_CONNECTION_STRING")).connect()
        self.db = client['dofus']
        self.collection: Collection
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

#    def find_by_repository_name(self, repository_name: str):
#        query = {
#            "$and": [
#                {"repo.name": repository_name},
#                {"type": "PullRequestEvent"}
#            ]
#        }
#
#        projection = {
#            "_id": 0,  # exclude MongoDB's default _id
#            "created_at": 1,
#            "repo.name": 1
#        }
#
#        results = self.collection.find(query, projection).sort("created_at", 1)
#
#        return list(results)
#
#    def find_by_pull_request_count(self):
#        pipeline = [
#            {
#                "$match": {
#                    "type": "PullRequestEvent"
#                }
#            },
#            {
#                "$group": {
#                    "_id": "$repo.name",
#                    "count": {"$sum": 1}
#                }
#            },
#            {
#                "$match": {
#                    "count": {"$gte": 2}
#                }
#            }
#        ]
#        # Run the aggregation
#
#        return list(self.collection.aggregate(pipeline))
#
#    def find_by_date_offset(self, offset_in_minutes: int) -> dict:
#        cutoff_time = datetime.now(UTC) - timedelta(minutes=offset_in_minutes)
#        pipeline = [
#            {
#                "$match": {
#                    "$expr": {
#                        "$gte": [
#                            {"$toDate": "$created_at"},  # convert string to date
#                            cutoff_time
#                        ]
#                    }
#                }
#            },
#            {
#                "$group": {
#                    "_id": "$type",
#                    "count": {"$sum": 1}
#                }
#            }
#        ]
#
#        results = list(self.collection.aggregate(pipeline))
#
#        grouped_results = {}
#        for result in results:
#            grouped_results[result["_id"]] = result["count"]
#
#        return grouped_results

class DofusPricesRepository:
    TABLE_PRICES = 'price'

    def __init__(self, table_name: str):
        client = MongoConnector(os.environ.get("MONGO_CONNECTION_STRING")).connect()
        self.db = client['dofus']
        self.collection: Collection
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
