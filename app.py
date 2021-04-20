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

template_dir = "frontend/templates"


app = Flask(__name__, template_folder=template_dir)



@app.route('/')
def index():
    """
    The root path of the application
    return: the root html file
    """
    return render_template('index.html',front_img="frontend/templates/images/index_image.png")

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


app.secret_key = "super secret key"  #tod-do change the key
app.register_blueprint(admin_app_page)
with app.app_context():
    set_database_config()
    current_app.db = get_mongo_database()

if __name__ == '__main__':
    app.run(threaded=True, port=5000 ,debug=True )