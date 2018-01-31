
""" 
copied from science-gateway-middleware/middleware/job/api.py
"""

import json_merge_patch
from flask_restful import Resource, abort, request




class SetupApi(Resource):
    """API endpoint called to setup a job on the cluster (POST)"""
    def __init__(self, **kwargs):
        # Inject job service
        self.jobs = kwargs['job_repository']
        self.middleware_only_fields = kwargs.get('middleware_only_fields')

    def abort_if_not_found(self, job_id):
        if not self.jobs.exists(job_id):
            abort(404, message="Job {} not found".format(job_id))

    def post(self, job_id):
        job_api = JobApi(job_repository=self.jobs,
                         middleware_only_fields=self.middleware_only_fields)
        updated_job = job_api._patch_job(job_id, request)
        manager = JIM(updated_job, job_repository=self.jobs)
        return manager.setup()



class ProgressApi(Resource):
    """
    API endpoint called to check the progress of a job
    on the cluster (POST)
    """
    def __init__(self, **kwargs):
        # Inject job service
        self.jobs = kwargs['job_repository']

    def get(self, job_id):

        job = self.jobs.get_by_id(job_id)
        if job:
            manager = JIM(job, job_repository=self.jobs)
            return manager.progress()
        else:
            abort(404, message="Job {} not found".format(job_id))


class DataApi(Resource):
    """API endpoint called to check the data of a job on the cluster (POST)"""
    def __init__(self, **kwargs):
        # Inject job service
        self.jobs = kwargs['job_repository']

    def get(self, job_id):

        job = self.jobs.get_by_id(job_id)
        if job:
            manager = JIM(job, job_repository=self.jobs)
            return manager.data()
        else:
            abort(404, message="Job {} not found".format(job_id))


class CancelApi(Resource):
    """API endpoint called to cancel a job on the cluster (POST)"""
    def __init__(self, **kwargs):
        # Inject job service
        self.jobs = kwargs['job_repository']

    def post(self, job_id):

        job = self.jobs.get_by_id(job_id)
        if job:
            manager = JIM(job, job_repository=self.jobs)
            return manager.cancel()
        else:
            abort(404, message="Job {} not found".format(job_id))


class RunApi(Resource):
    """API endpoint called to run a job on the cluster (POST)"""
    def __init__(self, **kwargs):
        # Inject job service
        self.jobs = kwargs['job_repository']
        self.middleware_only_fields = kwargs.get('middleware_only_fields')

    def abort_if_not_found(self, job_id):
        if not self.jobs.exists(job_id):
            abort(404, message="Job {} not found".format(job_id))

    def post(self, job_id):
        job_api = JobApi(job_repository=self.jobs,
                         middleware_only_fields=self.middleware_only_fields)
        updated_job = job_api._patch_job(job_id, request)
        manager = JIM(updated_job, job_repository=self.jobs)
        return manager.run()
