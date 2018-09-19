# Job Manager: Openfoam

Job manager for the Openfoam simulator

### Installation

To run the job manager.

```
(cd keys && ./create_keys.sh)
docker-compose up
```

### Configuration

Overwrite the configuration in `config.dev.json`. An example is provided in the file `config.example.json`.


This should be a standalone Flask app, that deals with running jobs on a
specific backend (in this case Openfoam).

Code that had previously been in science-gateway-middleware is now in
`tmp_reference/job_information_manager.py`
and seems to be a good starting point.


This package creates a flask app, with the API at `0.0.0.0:5010`.

This Flask app will communicate with the middleware passing HTTP verbs via the `requests` library.
There are (temporary) example API calls in `tmp_reference/example_requests_requests.py`


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
A PUT request to this endpoint will trigger a PUT request to the middleware, updating the status of a job.
The data should be a json object `{"status": <status>}`.


```
/job/<job_id>/output
```
A GET request to this endpoint will return an access token allowing retrieval of the job output.
