"""
Routes module
"""

from .job_routes import JobStartApi, JobStatusApi, JobOutputApi


def setup_routes(api):
    """
    Setup routes for API endpoints
    """
    api.add_resource(JobStartApi,'/job/<int:job_id>/start')

    api.add_resource(JobStatusApi,'/job/<int:job_id>/status')
    
    api.add_resource(JobOutputApi,'/job/<int:job_id>/output')