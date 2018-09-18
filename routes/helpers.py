"""
Helper functions for the routes
"""

from connection.constants import RequestStatus


def make_response(response=RequestStatus.SUCCESS, messages=[], errors=[], data=None):
    """
    Make a response dictionary to return to the user
    """
    return {
        "status": response.value,
        "messages": messages,
        "errors": errors,
        "data": data,
    }


class ResponseLog:
    """
    Aggregate errors and messages for reporting.
    """

    def __init__(self):
        self.messages = []
        self.errors = []

    def add_message(self, message):
        self.messages.append(message)

    def add_error(self, error):
        self.errors.append(error)
