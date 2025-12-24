from pymongo import MongoClient


class MongoConnector:

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def connect(self) -> MongoClient:
        client = MongoClient(self.connection_string)

        return client
