import logging

log = logging.getLogger()

import ftrack
import utils
import plugins_api

topic = 'ftrack.update'


def callback(event):

    #update task when version is updated
    for entity in event['data'].get('entities', []):
        #status updating
        if entity['entityType'] == 'assetversion' and entity['action'] == 'update' and entity['keys'][0]=='statusid':
            #variables
            version = ftrack.AssetVersion(id=entity['entityId'])
            project = version.getParents()[-1]
            task = version.getTask()

            #indexs for task statuses
            taskStateDict = {'NOT_STARTED': 'Not Started', 'IN_PROGRESS': 'In Progress',
                      'DONE': 'Complete', 'BLOCKED': 'On Hold'}

            taskOverrides = {'Blocking': 'Pending Review'}

            taskStatuses = project.getTaskStatuses()

            #getting statuses for states
            for state in taskStateDict:
                for status in taskStatuses:
                    if status.getName() == taskStateDict[state]:
                        taskStateDict[state] = status

            for state in taskStateDict:
                if isinstance(taskStateDict[state], str):
                    taskStateDict[state] = None

            #getting statuses for overrides
            for override in taskOverrides:
                for status in taskStatuses:
                    if status.getName() == taskOverrides[override]:
                        taskOverrides[override] = status

            for override in taskOverrides:
                if isinstance(taskOverrides[override], str):
                    taskOverrides[override] = None

            #seeing if any status can be reflected directly onto task
            statusUpdate = None
            for status in taskStatuses:
                if version.getStatus().getName() == status.getName():
                    statusUpdate = status

            #if not status found, try and find with overrides
            if not statusUpdate:
                for override in taskOverrides:
                    if override == version.getStatus().getName():
                        statusUpdate = taskOverrides[override]

            #if no status found, try and find with the states
            if not statusUpdate:
                for state in taskStateDict:
                    if state == version.getStatus().getState():
                        statusUpdate = taskStateDict[state]

            #setting status if any found
            if statusUpdate:
                task.setStatus(statusUpdate)
                log.info('Updating %s/%s to %s' % (task.getParent().getName(),
                                                task.getName(), statusUpdate.getName()))
            else:
                log.info('FAILED to update %s/%s' % (task.getParent().getName(),
                                                  task.getName()))

        #update thumbnail with first parent thumbnail
        if entity['entityType'] == 'task' and entity['action'] == 'add':
            task = ftrack.Task(id=entity['entityId'])
            if not task.get('thumbid'):

                thumbnail = utils.getThumbnailRecursive(task)
                task.setThumbnail(thumbnail)

                parent = task.getParent()
                log.info('Updating thumbnail for task %s/%s' % (parent.getName(), task.getName()))


def main(event):
    success = plugins_api.check_project(event, __file__)
    if success:
        callback(event)
