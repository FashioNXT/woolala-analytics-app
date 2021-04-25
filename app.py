"""
The main application file . The application uses several blueprints which are registered to the application in its context

"""
from flask import Flask , render_template, url_for, request, session, redirect
from blueprints.AdminAppBlueprint import admin_app_page
import bcrypt
import os
from flask import g, current_app
import configparser
from database_connection.DatabaseConnection import get_mongo_database
import datetime

import logging

template_dir = "frontend/templates"

app = Flask(__name__, template_folder=template_dir)


def set_basic_config():
    config = configparser.RawConfigParser()
    config.read('ConfigFile.properties')
    current_app.env = config.get('General', 'env')

def set_database_config():
    """
    Function to read the database configuartion fron properties file and add it to current app context
    """
    config = configparser.RawConfigParser()
    config.read('ConfigFile.properties')
    current_app.env = config.get('General', 'env')
    current_app.database_url = config.get('DatabaseSection', 'database.url')
    current_app.db_name = config.get('DatabaseSection', 'database.prod')
    if (current_app.env == "test"):
        current_app.db_name = config.get('DatabaseSection', 'database.test')

def set_log_config():
    """
    Fucntion to set logger settings for both file and console logging
    """
    if(os.path.exists(current_app.env+".log")):
        os.remove(current_app.env+".log")

    logFormatStr = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
    logging.basicConfig(format=logFormatStr, filename=current_app.env+".log", level=logging.DEBUG)
    # Create handlers
    formatter = logging.Formatter(logFormatStr, '%m-%d %H:%M:%S')
    fileHandler = logging.FileHandler(current_app.env+".log")
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.INFO)
    streamHandler.setFormatter(formatter)
    current_app.logger.addHandler(fileHandler)
    current_app.logger.addHandler(streamHandler)




app.secret_key = "super secret key"  #tod-do change the key
app.register_blueprint(admin_app_page)

with app.app_context():
    """
    current app context
    """
    set_basic_config()
    set_log_config()
    set_database_config()

    current_app.db = get_mongo_database()


@app.route('/')
def index():
    """
    The root path of the application
    return: the root html file
    """
    try:
      return render_template('index.html',front_img="frontend/templates/images/index_image.png")
    except:
        current_app.logger.exception("message")

if __name__ == '__main__':
    app.run(threaded=True, port=5000 ,debug=False )