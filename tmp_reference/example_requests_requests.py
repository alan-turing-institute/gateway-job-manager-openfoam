"""
TEMPORARY  example of some python commands using the requests library that can call the job manager API
"""

import requests


### start job 123 on job_manager,  send fields/values to patch, and locations of scripts that need to be patched

r=requests.post("http://localhost:5001/job/123/start", json={"fields_to_patch": [{"name" : "field1", "value": "val1"} ],"scripts": [{"name": "Allrun", "location" : "testopenfoamapi"}],"username" : "testuser"})

print(r.text)

### change status of job 123 to "Submitted"

r=requests.patch("http://localhost:5001/job/123/status",json={"job_status" : "Submitted"})

print r.text



###### CREATE NEW JOB IN MIDDLEWARE, FROM CASE 1:
r = requests.post("http://localhost:5000/job",json={"case_id":1, "name":"testjob","author":"testuser"})
###### START THAT JOB FROM MIDDLEWARE
r = requests.post("http://localhost:5000/job/1")
##### GET THAT JOBS STATUS FROM MIDDLEWARE
r = requests.post("http://localhost:5000/job/1/status")


