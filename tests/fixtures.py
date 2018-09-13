"""
Helpful fixtures for testing
"""
import os
from pathlib import Path
from flask import Flask
from flask_restful import Api
from pytest import fixture


@fixture(scope="module")
def demo_app():
    """
    Setup the flask app context I hope
    """
    app = Flask(__name__)

    # read general config from JSON

    config_fname = "config.testing.json"
    # assert Path(config_fname).is_file()
    app.config.from_json(config_fname)

    # read storage config from environment
    app.config["STORAGE_ACCOUNT_NAME"] = os.getenv("STORAGE_ACCOUNT_NAME", "")
    app.config["STORAGE_ACCOUNT_KEY"] = os.getenv("STORAGE_ACCOUNT_KEY", "")

    app.testing = True
    Api(app)

    return app
