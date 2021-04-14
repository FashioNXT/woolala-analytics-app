
from flask import Flask
from blueprints.admin_app_blueprint import admin_app_page
app = Flask(__name__)


@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.register_blueprint(admin_app_page)
    app.run(threaded=True, port=5000)