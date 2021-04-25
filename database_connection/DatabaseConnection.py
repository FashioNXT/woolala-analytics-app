from pymongo import MongoClient
import configparser
import base64
from flask import g,current_app
def get_mongo_database():
    """
    Function to connect to mongoDB in the current application context
    Returns: the db connection
    """
    current_app.logger.info("Establishing Database Connection")
    try:
        client = MongoClient(current_app.database_url)
        db = client[current_app.db_name]
        current_app.logger.info("Database Connected")
        return db
    except Exception:
        current_app.logger.exception("message")

