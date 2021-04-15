
from flask import Flask , render_template, url_for, request, session, redirect
from blueprints.admin_app_blueprint import admin_app_page
import bcrypt
import os
from flask import g, current_app
import configparser
from database_connection.database_connection import get_mongo_database

template_dir = "frontend/templates"
app = Flask(__name__, template_folder=template_dir)
app.secret_key = "super secret key"
app.register_blueprint(admin_app_page)



@app.route('/')
def index():

    return render_template('index.html')

def set_database_config():
    config = configparser.RawConfigParser()
    config.read('ConfigFile.properties')
    current_app.env = config.get('General', 'env')
    current_app.database_url = config.get('DatabaseSection', 'database.url')
    current_app.db_name = config.get('DatabaseSection', 'database.prod')
    if (current_app.env == "test"):
        current_app.db_name = config.get('DatabaseSection', 'database.test')


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    #app.register_blueprint(admin_app_page)
    with app.app_context():
        set_database_config()
        current_app.db = get_mongo_database()

    app.run(threaded=True, port=5000 ,debug=True )