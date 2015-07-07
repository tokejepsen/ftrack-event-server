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
            version_status = version.getStatus()
            try:
                task = ftrack.Task(version.get('taskid'))
            except:
                return
            task_status = None

            # Filter to versions with status change to "render queued"
            if version_status.get('name').lower() == 'pending changes':

                task_status = utils.GetStatusByName('pending changes')

            # Filter to versions with status change to "render queued"
            if version_status.get('name').lower() == 'render queued':

                task_status = utils.GetStatusByName('render')

            # Filter to versions with status change to "render"
            if version_status.get('name').lower() == 'render':

                task_status = utils.GetStatusByName('render')

            # Filter to versions with status change to "render complete"
            if version_status.get('name').lower() == 'render complete':

                task_status = utils.GetStatusByName('artist review')

            # Filter to versions with status change to "render failed"
            if version_status.get('name').lower() == 'render failed':

                task_status = utils.GetStatusByName('render failed')

            # Filter to versions with status change to "render failed"
            if version_status.get('name').lower() == 'proposed final':

                task_status = utils.GetStatusByName('proposed final')

            # Proceed if the task status was set
            if task_status:
                # Get path to task
                path = task.get('name')
                for p in task.getParents():
                    path = p.get('name') + '/' + path

                # Setting task status
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
