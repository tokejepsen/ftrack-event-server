import os
import logging

log = logging.getLogger(__name__)

import ftrack


def check_project(event, file):
    path = os.path.dirname(__file__)
    plugin_project = os.path.dirname(file).replace(path, '')
    plugin_project = plugin_project.split(os.sep)

    if len(plugin_project) != 2:
        plugin_project = plugin_project[-1]
    else:
        return True

    for entity in event['data'].get('entities', []):
        try:
            for p in entity['parents']:
                if p['entityType'] == 'show':
                    project = ftrack.Project(id=p['entityId'])
                    if project.get('name') != plugin_project:
                        return False
        except:
            pass

    return True
