import logging

log = logging.getLogger()

import ftrack
import plugins_api
import utils
reload(utils)

topic = 'ftrack.update'


def callback(event):
    """ This plugin sets the task status from the version status update.
    """

    for entity in event['data'].get('entities', []):

        # Filter non-assetversions
        if entity.get('entityType') == 'assetversion' and entity['action'] == 'add':
            version = ftrack.AssetVersion(id=entity.get('entityId'))
            version_status = version.getStatus()

            type_name = utils.GetAssetNameById(version.getAsset().get('typeid'))

            # Checking if its a compositing asset type, child of a shot and
            # if there is only one task on the shot
            check = False
            if type_name.lower() == 'compositing':

                shot = None
                for p in version.getParents():
                    try:
                        if p.get('objecttypename') == 'Shot':
                            shot = p
                            break
                    except:
                        pass

                if shot:
                    tasks = shot.getTasks()
                    if len(tasks) == 1:
                        check = True

            # Setting the task status to "ready", if task status is "not ready"
            if check:
                task = ftrack.Task(version.get('taskid'))

                if task.getStatus().get('name').lower() == 'not ready':

                    # Get path to task
                    path = task.get('name')
                    for p in task.getParents():
                        path = p.get('name') + '/' + path

                    # Setting task status
                    task_status = utils.GetStatusByName('ready')
                    try:
                        task.setStatus(task_status)
                    except Exception as e:
                        log.error('%s status couldnt be set: %s' % (path, e))
                    else:
                        log.info('%s updated to "%s"' % (path, task_status.get('name')))


def main(event):
    success = plugins_api.check_project(event, __file__)
    if success:
        callback(event)
