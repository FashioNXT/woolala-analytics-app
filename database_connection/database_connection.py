from pymongo import MongoClient
import configparser
import base64
from flask import g
def get_mongo_database():

    client = MongoClient(g.database_url)
    db = client[g.db_name]

    return db

