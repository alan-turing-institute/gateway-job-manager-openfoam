"""
Routes module
"""

from .job_routes import JobStartApi, JobStatusApi, JobOutputApi
from .fake_routes import TestApi


def setup_routes(api):
    """
    Setup routes for API endpoints
    """
    api.add_resource(JobStartApi, "/job/<string:job_id>/start")

    api.add_resource(JobStatusApi, "/job/<string:job_id>/status")

    api.add_resource(JobOutputApi, "/job/<string:job_id>/output")

    api.add_resource(TestApi, "/test")
