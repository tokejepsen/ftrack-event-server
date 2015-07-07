import os
import logging

log = logging.getLogger()

import ftrack
import plugins_api

topic = 'ftrack.update'


def callback(event):
    """This plugin remove any editing task created underneath a shot.
    This is subpress the Hiero workflow of adding an editing task to
    all shots created.
    """

    # update task when version is added
    for entity in event['data'].get('entities', []):

        # filter to updating tasks
        if entity['entityType'] == 'task' and entity['action'] == 'add':
            task = ftrack.Task(id=entity['entityId'])

            # filter to tasks, not shots or sequences
            if task.get('objecttypename') == 'Task':

                # check that the task is child of a shot
                check = False
                if task.getParent().get('objecttypename') == 'Shot':
                    check = True

                # check that its an editing task
                if check:
                    check = False
                    for t in ftrack.getTaskTypes():
                        if task.get('typeid') == t.get('typeid'):
                            if t.get('name').lower() == 'editing':
                                check = True

                # Deleting task
                if check:

                    task.delete()

                    # Get path to shot
                    path = task.get('name')
                    try:
                        for p in task.getParents():
                            path = p.get('name') + '/' + path
                    except:
                        pass

                    log.info('Deleted %s' % path)


def main(event):
    success = plugins_api.check_project(event, __file__)
    if success:
        callback(event)
