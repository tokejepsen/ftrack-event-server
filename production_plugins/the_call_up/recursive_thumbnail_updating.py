import os
import logging

log = logging.getLogger()

import ftrack
import plugins_api
import utils
reload(utils)

topic = 'ftrack.update'


def callback(event):
    """ This plugin creates a thumbnail from the first available thumbnail in the entity's parents.
    """

    # update task when version is updated
    for entity in event['data'].get('entities', []):

        # update thumbnail with first parent thumbnail
        if entity['entityType'] == 'task' and entity['action'] == 'add':
            try:
                task = ftrack.Task(id=entity['entityId'])
            except:
                continue

            if not task.get('thumbid'):

                thumbnail = utils.getThumbnailRecursive(task)
                if thumbnail:
                    task.setThumbnail(thumbnail)

                    parent = task.getParent()
                    log.info('Updating thumbnail for task %s/%s' % (parent.getName(), task.getName()))

def main(event):
    success = plugins_api.check_project(event, __file__)
    if success:
        callback(event)
