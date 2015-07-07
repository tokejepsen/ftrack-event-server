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
        if entity['entityType'] == 'assetversion' and entity['action'] == 'update' and (entity['keys'][0]=='statusid' or entity['keys'][0]=='ispublished'):
            version = ftrack.AssetVersion(id=entity.get('entityId'))
            version_status = version.getStatus()
            task = ftrack.Task(version.get('taskid'))
            task_status = None
            assetType = version.getAsset().getType().getName()
            comment = version.getComment()

            if assetType == 'Animation':
                # Filter to versions with status change to "pending review"
                if version_status.get('name').lower() == 'pending review':

                    task_status = utils.GetStatusByName('pending review')

                # Filter to versions with status change to "reviewed"
                if version_status.get('name').lower() == 'reviewed':
                    if comment.startswith('BLOCKING'):
                        task_status = utils.GetStatusByName('blocking')
                    else:
                        task_status = utils.GetStatusByName('animating')

                # Filter to versions with status change to "approved"
                if version_status.get('name').lower() == 'approved':
                    if comment.startswith('BLOCKING'):
                        task_status = utils.GetStatusByName('animating')
                    else:
                        task_status = utils.GetStatusByName('complete')


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
