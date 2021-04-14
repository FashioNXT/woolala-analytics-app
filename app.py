
from flask import Flask
from blueprints.crm_blueprint import crm_page
app = Flask(__name__)


@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.register_blueprint(crm_page)
    app.run(threaded=True, port=5000)