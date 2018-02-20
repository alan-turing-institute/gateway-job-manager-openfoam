# science-gateway-job-manager-blue

job manager for the Blue simulator


This should be a standalone Flask app, that deals with running jobs on a
specific backend (in this case Blue).

Start by looking at what is there in science-gateway-middleware.
`middleware/job_information_manager.py`
seems to be a good starting point.

Create a new app.py and factory.py with a `create_app` function, and fill bits
in as I come to understand them...

To build the docker image (first time use, or after changing the code), from this directory:
```
docker build -t job-manager-blue .
```

To run the docker container:
```
docker run -it job-manager-blue
```
This should run the flask app, with the API at `0.0.0.0:5001`.

This Flask app will communicate with the middleware passing HTTP verbs via the `requests` library.
There are (temporary) example API calls in `example_requests_requests.py`







