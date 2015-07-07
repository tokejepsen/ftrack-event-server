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
                if task.getStatus().get('name').lower() == 'supervisor review':
                    check = True

            if check:
                version_number = 0
                version_latest = None
                for version in task.getAssetVersions():
                    if version.getAsset().getType().getShort() == 'img' and \
                    version.getVersion() > version_number:
                        version_number = version.getVersion()
                        version_latest = version

                if version_latest:
                    status = utils.GetStatusByName('supervisor review')
                    version_latest.setStatus(status)

                    path = task.getParent().getName() + '/'
                    path += version_latest.getAsset().getName() + ' '
                    path += 'v%s' % str(version_latest.getVersion()).zfill(2)
                    log.info('Setting %s to "Supervisor Review"' % path)


def main(event):
    success = plugins_api.check_project(event, __file__)
    if success:
        callback(event)
