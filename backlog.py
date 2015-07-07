import sys
import datetime
import logging
import os
import json

sys.path.append(r'K:\tools\FTrack\ftrack-api')

import ftrack
ftrack.setup()


logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

path = os.path.dirname(__file__)
backlog_file = os.path.join(path, 'backlogs' 'backlog.json')


def callback(event):
    '''Event callback printing all new or updated entities.'''

    t = datetime.datetime.now()
    format = "%Y-%m-%d-%H-%M-%S"
    data = event.copy()
    data['datetime'] = t.strftime(format)

    with open(backlog_file, mode='r') as json_file:
        json_data = json.load(json_file)

    json_data.append(data)

    with open(backlog_file, mode='w') as json_file:
        json.dump(json_data, json_file, indent=2)

# Subscribe to events with the update topic.
ftrack.EVENT_HUB.subscribe('topic=*', callback)
ftrack.EVENT_HUB.wait()
