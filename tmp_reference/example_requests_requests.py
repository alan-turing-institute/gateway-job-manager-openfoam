"""
TEMPORARY  example of some python commands using the requests library that can call the job manager API
"""

import requests


### start job 123,  send fields/values to patch, and locations of scripts that need to be patched

r=requests.post("http://localhost:5001/job/123/start", json={"fields_to_patch": [{"name" : "field1", "value": "val1"} ],"scripts": [{"name": "script1", "location" : "www.madeupscripts.com"}],"username" : "testuser"})

print(r.text)

### change status of job 123 to "Submitted"

r=requests.patch("http://localhost:5001/job/123/status",json={"job_status" : "Submitted"})

print r.text

                 
