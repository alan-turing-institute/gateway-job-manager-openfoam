#! /usr/bin/env python3
"""
The main entry point for this flask app
"""

import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from routes import setup_routes

config = {
    "development": "config.DevelopmentConfig",
    "testing": "config.TestingConfig",
    "production": "config.ProductionConfig",
    "default": "config.DevelopmentConfig"
}

def configure_app(app):
    config_name = os.getenv('FLASK_CONFIGURATION', 'default')
    app.config.from_object(config[config_name])
    app.config.from_pyfile('config.cfg', silent=True)

app = Flask(__name__, instance_relative_config=True)
configure_app(app)

api = Api(app)
CORS(app, resources={r'/*': {'origins': '*'}})

setup_routes(api)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
