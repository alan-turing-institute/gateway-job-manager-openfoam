"""
Constants and utilites module
"""

from enum import Enum

from werkzeug.routing import BaseConverter


class JobStatus(Enum):
    """
    Job status enum. Variable must always be UPPERCASE.
    """

    FAILED = "Failed"
    RUNNING = "Running"
    FINALIZING = "Finalizing"
    COMPLETED = "Completed"
    NOT_STARTED = "Not Started"
    QUEUED = "Queued"
    STOPPED = "Stopped"


class StatusConverter(BaseConverter):
    """
    Flask url converter for Status enums
    """

    def to_python(self, value: str):
        """
        Convert the string from the URL to an enum
        """
        return JobStatus[value.upper()]

    def to_url(self, value: JobStatus):
        """
        Convert the enum to the url representation
        """
        return value.name


class RequestStatus(Enum):
    """
    A request status enum
    """

    SUCCESS = "success"
    FAILED = "failed"
