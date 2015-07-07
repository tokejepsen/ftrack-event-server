import logging

log = logging.getLogger()

import ftrack
import plugins_api

topic = 'ftrack.update'


def callback(event):
    """ This plugin sets the shot status from the task status update.
    """

    for entity in event['data'].get('entities', []):

        # Filter non-tasks
        if entity.get('entityType') == 'task' and entity['action'] == 'update':

            # Find task if it exists
            task = None
            try:
                task = ftrack.Task(id=entity.get('entityId'))
            except:
                return

            # filter out shots and sequences
            if task and task.get('objecttypename') == 'Task':

                # Getting shot and setting status
                shot = ftrack.Shot(id=entity.get('parents')[1].get('entityId'))
                shot.setStatus(task.getStatus())

                # Get path to shot
                path = shot.get('name')
                for p in shot.getParents():
                    path = p.get('name') + '/' + path

                log.info('%s updated to "%s"' % (path,
                                                 task.getStatus().get('name')))


def main(event):
    success = plugins_api.check_project(event, __file__)
    if success:
        callback(event)
