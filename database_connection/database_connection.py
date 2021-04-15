from pymongo import MongoClient
import configparser
import base64
from flask import g,current_app
def get_mongo_database():

    client = MongoClient(current_app.database_url)
    db = client[current_app.db_name]

    return db

