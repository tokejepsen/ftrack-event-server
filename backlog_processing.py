import os
import json
from pprint import pprint

path = os.path.dirname(__file__)
backlog = os.path.join(path, 'backlog.json')

with open(backlog) as json_data:
    d = json.load(json_data)
    print d
