from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv

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
        self._client = MongoClient(conn_string)
        self._db = self._client.eco_social

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