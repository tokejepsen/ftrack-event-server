import logging

log = logging.getLogger()

import ftrack
import plugins_api
import utils

topic = 'ftrack.update'


def callback(event):
    """ This plugin sets the task status from the version status update.
    """

    for entity in event['data'].get('entities', []):

        # Filter non-assetversions
        if entity.get('entityType') == 'task' and entity['action'] == 'update':

            # Find task if it exists
            task = None
            try:
                task = ftrack.Task(id=entity.get('entityId'))
            except:
                return

            # Filter to tasks with complete status
            check = False
            if task and task.get('objecttypename') == 'Task':
                if task.getStatus().get('name').lower() == 'complete' and \
                task.getName().lower() == 'compositing':
                    check = True

            if check:
                # Get path to task
                path = task.get('name')
                for p in task.getParents():
                    path = p.get('name') + '/' + path

                # Setting next task status
                try:
                    task.setStatus(utils.GetStatusByName('supervisor review'))
                except Exception as e:
                    log.error('%s status couldnt be set: %s' % (path, e))
                else:
                    log.info('%s updated to "Ready"' % path)


def main(event):
    success = plugins_api.check_project(event, __file__)
    if success:
        callback(event)
