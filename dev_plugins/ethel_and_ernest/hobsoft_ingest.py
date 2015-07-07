import os
import re
import shutil
import logging
import traceback

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
            asset = version.getAsset()

            if version.getVersion() != 1 or asset.getName() != 'hobsoft':
                return

            shot = asset.getParent()
            task = None
            if shot.getTasks(taskTypes=['painting']):
                task = shot.getTasks(taskTypes=['painting'])[0]
            else:
                task_type = utils.GetTaskTypeByName('painting')
                status = utils.GetStatusByName('ready')
                task = shot.createTask('painting', taskType=task_type,
                                        taskStatus=status)

            new_asset = shot.createAsset('painting', 'img', task=task.getId())
            new_version = new_asset.createVersion()

            version_dir = r'L:\ethel_and_ernest_0001\renders\img_sequences'
            version_name = 'v%s' % str(new_version.getVersion()).zfill(3)
            version_dir = os.path.join(version_dir, shot.getName(), 'painting',
                                        version_name)

            for c in version.getComponents():
                path = c.getFilesystemPath()

                current_dir = os.path.join(version_dir, c.getName())
                if not os.path.exists(current_dir):
                    os.makedirs(current_dir)

                for f in os.listdir(os.path.dirname(path)):
                    s = os.path.join(os.path.dirname(path), f)
                    d = os.path.join(current_dir, f)

                    shutil.copy2(s, d)

                new_path = os.path.join(current_dir, os.path.basename(path))
                new_version.createComponent(name=c.getName(), path=new_path)

            new_version.publish()
            log.info('Created new version: %s' % new_version)

def main(event):
    success = plugins_api.check_project(event, __file__)
    if success:
        callback(event)
