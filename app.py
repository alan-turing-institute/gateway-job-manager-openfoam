import os
from factory import create_app

from flask import Flask
from flask_restful import Api
from flask_cors import CORS


from routes import setup_routes


config_name = os.environ.get('APP_CONFIG_NAME')
if not config_name:
    config_name = 'test'
app = create_app(config_name)

api = Api(app)
CORS(app, resources={r'/*': {'origins': '*'}})

setup_routes(api)

if __name__ == "__main__":
    app.run(host="localhost",port="5001")
