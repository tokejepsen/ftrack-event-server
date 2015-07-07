#Notes
- all folder needs to have ```__init__.py```
- all plugins need to have this structure:

```python
import logging

log = logging.getLogger()

import ftrack
import plugins_api

topic = 'ftrack.update'


def callback(event):
    # update task when version is updated
    for entity in event['data'].get('entities', []):

        # update thumbnail with first parent thumbnail
        if entity['entityType'] == 'task' and entity['action'] == 'update':
            log.info('Calling from a project!')


def main(event):
    success = plugins_api.check_project(event, __file__)
    if success:
        callback(event)
```
- setting up a server has this structure:
  - ```example_plugins``` folder already exists within ftrack-event-server repo
  - ```example_plugins``` folder contains ```__init__.py```

```python
import os
import server

os.environ['LOGNAME'] = 'toke.jepsen'
server.setup('example_plugins')
```
- create project folder separately from creating files
  - doesn't register when copying whole folder with files across
