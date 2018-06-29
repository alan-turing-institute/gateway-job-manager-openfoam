#! /usr/bin/env python3
"""
The main entry point for this flask app
"""

import os
from pathlib import Path
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from routes import setup_routes

app = Flask(__name__)
config_mode = os.getenv('FLASK_CONFIGURATION', 'development')

# read general config from JSON
config_fname = 'config.{}.json'.format(config_mode.lower())
app.config.from_json(config_fname)

# read storage config from environment
app.config['STORAGE_ACCOUNT_NAME'] = os.getenv('STORAGE_ACCOUNT_NAME', '')
app.config['STORAGE_ACCOUNT_KEY'] = os.getenv('STORAGE_ACCOUNT_KEY', '')

api = Api(app)
CORS(app, resources={r'/*': {'origins': '*'}})

setup_routes(api)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
