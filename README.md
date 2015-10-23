####Writing plugins####

- all plugin folders need to have `__init__.py`
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

In case you don't wont the plugin to be filtered by project, rename your `callback` method to `main` and remove the last four lines from the example (so you don't have 2 `main` methods in the plugin.)

####Registering plugins####
To register plugins with the event server you have 2 options:
- create environment variable named `FTRACK_EVENT_SERVER_PLUGINS` which points to the root folder with your plugins
- pass the absolute path to the plugin folder as an argument when running the server
Plugin folder passed as an argument always takes priority, so you can use it as an override for the environment variable. This can be usefull for temporarily loading development plugins for example.


####Setting up server####

To be able to run the server you need to have properly configured ftrack api on your system. To do that you can follow [ftrack api documentation](http://ftrack.rtd.ftrack.com/en/latest/developing/getting_started.html)
