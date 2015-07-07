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
        if entity['entityType'] == 'assetversion' and entity['action'] == 'add':
            version = ftrack.AssetVersion(id=entity.get('entityId'))
            task = ftrack.Task(version.get('taskid'))
            current_task_status = task.getStatus().getName()

            if current_task_status.lower() == 'blocking':
                comment = version.getComment()
                comment = 'BLOCKING: ' + comment
                version.set('comment', value=comment)


def main(event):
    success = plugins_api.check_project(event, __file__)
    if success:
        callback(event)
