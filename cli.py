import json
import os
import threading
from glob import glob

import fire
import requests
from pyblast.schema import SequenceSchema

from config import ConfigRegistry
from dasi import create_app
from dasi.graphql_schema.query_formatter import fmt_mutation
import time

class App(object):

    def __init__(self, env, env_variables=None):
        app = create_app(env_variables=env_variables, config=env)
        self.app = app
        self.running = False

    def run(self, host="0.0.0.0", port=5000, thread=False):
        self.host = host
        self.port = port
        if thread:
            thread = threading.Thread(target=self.app.run, kwargs={'host': host, 'port': port})
            thread.daemon = True
            thread.start()
            self.running = True
            print(self.running)
            time.sleep(2)
            return self
        else:
            self.app.run()

    def envs(self):
        return ["config." + n for n in ConfigRegistry.models.keys()]

    @staticmethod
    def _parse_to_json(file, filename, parser_host="http://0.0.0.0", parser_port=3000):
        """Sends a request to the graphql parser to parse a file"""

        parser_query = """
        query ParseSequences($file: String!, $filename: String!) {
          tojson(file: $file, filename: $filename) {
            messages
            parsedSequence {
              name
              sequence
              circular
              description
              features {
                name
                type
                id
                start
                end
                strand
              }
            }
            success
          }
        }
        """

        url = "{}:{}/graphql".format(parser_host, parser_port)
        variables = {
            "file": file,
            "filename": filename
        }
        payload = {"query": parser_query, "variables": variables}
        headers = {'content-type': 'application/json'}
        try:
            return requests.post(url, data=json.dumps(payload), headers=headers)
        except Exception as e:
            raise Exception(
                "Could not connect to parsing_service at {}:{}. Are you sure its running?".format(parser_host,
                                                                                                  parser_port))

    def _create_sequence(self, data, host=None, port=None):
        if host is None:
            host = self.host
        if port is None:
            port = self.port
        url = "http://{}:{}/graphql".format(host, port)
        print(url)
        fields = """
                sequence {
                    id
                    name
                    bases
                    description
                    circular
                    features {
                        edges {
                            node {
                                id
                                name
                                start
                                end
                                type
                                strand
                            }
                        }
                    }
                }
        """
        # for f in data['features']:
        #     if 'id' in f and f['id'] is None:
        #         del f['id']
        schema = SequenceSchema()
        loaded = schema.load(data)
        for f in loaded['features']:
            if 'id' in f:
                del f['id']
        mutation, variables = fmt_mutation("createSequence", {"sequence": ("SequenceInput!", loaded)}, fields)
        payload = {"query": mutation, "variables": variables}
        headers = {"content-type": "application/json"}
        return requests.post(url, data=json.dumps(payload), headers=headers)

    def populate_database(self, directory, host, port):
        sequences = []
        print(directory)
        print(glob(os.path.join(directory, "*.gb")))
        for path in glob(os.path.join(directory, "*.gb")):
            with open(path, 'r') as f:
                res = self._parse_to_json(f.read(), os.path.basename(path))
                seq = res.json()['data']['tojson']['parsedSequence']
                sequences.append(seq)
        for seq in sequences:
            self._create_sequence(seq, host, port)
            print(res.json())


if __name__ == '__main__':
    fire.Fire(App)
