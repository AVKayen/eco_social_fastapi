from pymongo.mongo_client import MongoClient
from pymongo.synchronous.database import Database
from pymongo.synchronous.collection import Collection
from typing import Any

from config.settings import settings


class Session:
    def __init__(self, conn_string: str):
        self._client: MongoClient[dict[str, Any]] = MongoClient(conn_string)
        self._db = self._client.get_database('eco_social')

        # Check if the connection is valid
        self._client.server_info()
        print('Connected to the MongoDB')

    def db(self) -> Database:
        return self._db

    def users_collection(self) -> Collection:
        return self._db.users

    def activities_collection(self) -> Collection:
        return self._db.activities


session: Session = Session(settings.db_uri)
