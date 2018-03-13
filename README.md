# Job Manager: Blue

Job manager for the Blue simulator

### Installation

To run the job manager.

```
(cd keys && ./create_keys.sh)
docker-compose up
```

### Configuration

Overwrite the configuration in `instance/config.cfg`. An example is provided in the file `instance/config.cfg.example`.


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


The following routes are implemented:
```
/job/job_id/start
```
a POST on this endpoint will start a job with id=job_id.  The 
data to be sent should be a json object with the following format:
```
{"fields_to_patch": [
			{
			"name" : <field_name>,
			"value": <val>
			},
			...
		],
"scripts" : [
		{
		"name" : <script_name>,
		"location" : <script_location>
		},
		...
	]
}
```

```
/job/<job_id>/status
```
A PATCH request to this endpoint will trigger a PATCH request to the middleware, updating the status of a job.
The data should be a json object `{"job_status": <status>}`.


```
/job/<job_id>/output
```
A GET request to this endpoint will return an access token allowing retrieval of the job output.



