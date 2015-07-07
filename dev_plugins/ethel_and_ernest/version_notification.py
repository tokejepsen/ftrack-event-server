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
        if entity.get('entityType') == 'assetversion' and entity['action'] == 'update':
            version = ftrack.AssetVersion(id=entity.get('entityId'))
            asset = version.getParent()

            # skipping if its not the first version
            if version.getVersion() != 1:
                return

            shot = asset.getParent()
            comp_tasks = shot.getTasks(taskTypes=['Compositing'])

            task = None

            # making a compositing task if non exists
            if not comp_tasks:
                task_type = utils.GetTaskTypeByName('compositing')
                task_status = utils.GetStatusByName('ready')

                task = shot.createTask('compositing', taskType=task_type,
                                        taskStatus=task_status)

                msg = '"compositing" task created on: %s' % shot.getName()
                log.info(msg)

                msg = 'Event Server (%s):\n\n' % __file__
                msg += '"compositing" task created.'
                shot.createNote(msg)
            else:
                # searching through tasks for compositing
                for t in comp_tasks:
                    if t.getName().lower() == 'compositing':
                        task = t

            if task:
                msg = 'Event Server (%s):\n\n' % __file__
                msg += 'First version of "%s" ready.' % asset.getName()
                task.createNote(msg)
            else:
                msg = 'No "compositing" task found on: %s' % shot.getName()
                log.warning(msg)

                msg = 'Event Server (%s):\n\n' % __file__
                msg += 'No "compositing" task found.'
                shot.createNote(msg)

def main(event):
    success = plugins_api.check_project(event, __file__)
    if success:
        callback(event)
