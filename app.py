
from flask import Flask , render_template, url_for, request, session, redirect
from blueprints.admin_app_blueprint import admin_app_page
import bcrypt
import os
from flask import g
import configparser
from database_connection.database_connection import get_mongo_database

template_dir = "frontend/templates"
app = Flask(__name__, template_folder=template_dir)





@app.route('/')
def index():

    return render_template('index.html')

def set_database_config():
    config = configparser.RawConfigParser()
    config.read('ConfigFile.properties')
    g.env = config.get('General', 'env')
    g.database_url = config.get('DatabaseSection', 'database.url')
    g.db_name = config.get('DatabaseSection', 'database.prod')
    if (g.env == "Test"):
        g.db_name = config.get('DatabaseSection', 'database.test')


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    with app.app_context():
        set_database_config()
        g.db = get_mongo_database()
    app.register_blueprint(admin_app_page)
    app.run(threaded=True, port=5000 )