from pymongo import MongoClient
import configparser
import base64
def get_database(env=None):

    config = configparser.RawConfigParser()
    config.read('../ConfigFile.properties')
    client = MongoClient(config.get('DatabaseSection', 'database.url'))

    client = MongoClient(
        "mongodb+srv://Developer_1:Developer_1@woolalacluster.o4vv6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    if(env=="test"):
        db = client[config.get('DatabaseSection', 'database.test')]
    else:

      db = client[config.get('DatabaseSection', 'database.prod')]

    return db

get_database()