from flask import Flask
from flask_restful import Api, Resource
from flask_cors import CORS

import json

##import job_information_manager as JIM


def create_app(config_name):
    app = Flask(__name__, instance_relative_config = True)
    CORS(app, resources={r"/api/*": {"origins": "*"}})


    #
    # ...
    #

   # class Helloworld(Resource):
   #     return
    
    api = Api(app)

    #
    # ...
    #

    return app
