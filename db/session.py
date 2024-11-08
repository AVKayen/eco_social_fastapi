from pymongo.mongo_client import MongoClient
from typing import Any
from dotenv import load_dotenv
from typing import Dict

import os


ENV_NAME = 'DB_URI'


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
        self._client: MongoClient[Dict[str, Any]] = MongoClient(conn_string)
        self._db = self._client.get_database('eco_social')
        print('Connected to the MongoDB')

        # for collection in self._db.list_collections():
        #     print(collection)

    # def create_collection(self, name: str, validator: dict):
    #     self._db.create_collection(name)
    #     self._db.command('collMod', name, validator=validator)

    def db(self):
        return self._db

    def users_collection(self):
        return self._db.users

    def activities_collection(self):
        return self._db.activities


load_dotenv()
conn_str = os.getenv(ENV_NAME)
if not conn_str:
    raise Exception('No connection string for MongoDB specified.')
session: Session = Session(conn_str)
