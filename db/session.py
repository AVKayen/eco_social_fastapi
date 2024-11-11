from pymongo.mongo_client import MongoClient
from pymongo.synchronous.database import Database
from pymongo.synchronous.collection import Collection
from typing import Any

from config.settings import settings


# COLLECTIONS = [
#     {
#         'name': 'users',
#         'validator': {
#             '$jsonSchema': {
#                 'bsonType': 'object',
#                 'required': ['username', 'password_hash'],
#                 'properties': {
#                     'username': {
#                         'bsonType': 'string',
#                     },
#                     'password_hash': {
#                         'bsonType': 'string',
#                     }
#                 }
#             }
#         }
#     }
# ]


class Session:
    def __init__(self, conn_string: str):
        self._client: MongoClient[dict[str, Any]] = MongoClient(conn_string)
        self._db = self._client.get_database('eco_social')
        print('Connected to the MongoDB')

        # for collection in self._db.list_collections():
        #     print(collection)

    # def create_collection(self, name: str, validator: dict):
    #     self._db.create_collection(name)
    #     self._db.command('collMod', name, validator=validator)

    def db(self) -> Database:
        return self._db

    def users_collection(self) -> Collection:
        return self._db.users

    def activities_collection(self) -> Collection:
        return self._db.activities


session: Session = Session(settings.db_uri)
