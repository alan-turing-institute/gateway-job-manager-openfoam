"""
Make some fake routes for testing purposes
"""

from flask_restful import Resource

class Test(Resource):
    """
    Class to be used for generating fake data
    """
    def get(self):
        return {'foo': 'bar'}
