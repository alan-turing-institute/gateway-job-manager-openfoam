"""
Routes module
"""

from .job_routes import JobStartApi


def setup_routes(api):
    """
    Setup routes for API endpoints
    """
    api.add_resource(JobStartApi,'/job/<int:job_id>/start')

    
