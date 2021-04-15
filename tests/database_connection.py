from pymongo import MongoClient
import configparser
import base64
def get_database(env=None):

    config = configparser.RawConfigParser()
    config.read('../ConfigFile.properties')
    client = MongoClient(config.get('DatabaseSection', 'database.url'))


    if(env=="test"):
        db = client[config.get('DatabaseSection', 'database.test')]
    else:

      db = client[config.get('DatabaseSection', 'database.prod')]
    return db

