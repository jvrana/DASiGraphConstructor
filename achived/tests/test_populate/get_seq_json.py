
import json
PORT = 5000

import requests

url = "http://0.0.0.0:{}/graphql".format(PORT)

mutation = """
    mutation createResults(queryId: "U2VxdWVuY2VzOjM=") {
        ok
        results {
            id
        }
    }
"""

payload = {
    "query": mutation
}
headers = {"content-type": "application/json"}

result = requests.post(url, data=json.dumps(payload), headers=headers)

print(result)