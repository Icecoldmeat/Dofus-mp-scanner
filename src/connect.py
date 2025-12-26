import os
from typing import Literal

from pymongo import MongoClient
from sqlalchemy import create_engine, Engine


class MongoConnector:

    def connect(self) -> MongoClient:
        client = MongoClient(os.environ.get("MONGO_CONNECTION_STRING"))

        return client


class SqlAlchemyConnector:

    def connect(self, connect_to: Literal["mysql", "postgresql"]) -> Engine:
        engine = None
        if connect_to == "mysql":
            engine = create_engine(os.environ.get("MYSQL_CONNECTION_STRING"))

        if connect_to == "postgresql":
            engine = create_engine(os.environ.get("POSTGRES_CONNECTION_STRING"))

        if engine is None:
            raise Exception("engine is not defined")

        return engine
