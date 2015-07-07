import os
import logging

log = logging.getLogger()

import ftrack
import plugins_api

topic = 'ftrack.update'


def callback(event):
    # update task when version is updated
    for entity in event['data'].get('entities', []):

        # update thumbnail with first parent thumbnail
        if entity['entityType'] == 'task' and entity['action'] == 'update':
            log.info('Calling from all projects!')


def main(event):
    success = plugins_api.check_project(event, __file__)
    if success:
        callback(event)
