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


def version_get(string, prefix, suffix = None):
  """Extract version information from filenames used by DD (and Weta, apparently)
  These are _v# or /v# or .v# where v is a prefix string, in our case
  we use "v" for render version and "c" for camera track version.
  See the version.py and camera.py plugins for usage."""

  if string is None:
    raise ValueError, "Empty version string - no match"

  regex = "[/_.]"+prefix+"\d+"
  matches = re.findall(regex, string, re.IGNORECASE)
  if not len(matches):
    msg = "No \"_"+prefix+"#\" found in \""+string+"\""
    raise ValueError, msg
  return (matches[-1:][0][1], re.search("\d+", matches[-1:][0]).group())


def version_set(string, prefix, oldintval, newintval):
  """Changes version information from filenames used by DD (and Weta, apparently)
  These are _v# or /v# or .v# where v is a prefix string, in our case
  we use "v" for render version and "c" for camera track version.
  See the version.py and camera.py plugins for usage."""

  regex = "[/_.]"+prefix+"\d+"
  matches = re.findall(regex, string, re.IGNORECASE)
  if not len(matches):
    return ""

  # Filter to retain only version strings with matching numbers
  matches = filter(lambda s: int(s[2:]) == oldintval, matches)

  # Replace all version strings with matching numbers
  for match in matches:
    # use expression instead of expr so 0 prefix does not make octal
    fmt = "%%(#)0%dd" % (len(match) - 2)
    newfullvalue = match[0] + prefix + str(fmt % {"#": newintval})
    string = re.sub(match, newfullvalue, string)
  return string

def get_version_up(path):
    (prefix, v) = version_get(path, 'v')
    v = int(v)
    return version_set(path, prefix, v, v + 1)

def version_up(path):
    new_path = get_version_up(path)

    if not os.path.exists(os.path.dirname(new_path)):
        os.makedirs(os.path.dirname(new_path))

    if not os.path.exists(new_path):
        shutil.copy(path, new_path)

    (prefix, v) = version_get(path, 'v')
    v = int(v)

    return [new_path, v]


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

            # Filter to tasks with "pending changes" status
            check = False
            if task and task.get('objecttypename') == 'Task':
                if task.getStatus().get('name').lower() == 'pending changes':
                    check = True

            # check that its an compositing task
            if check:
                check = False
                for t in ftrack.getTaskTypes():
                    if task.get('typeid') == t.get('typeid'):
                        if t.get('name').lower() == 'compositing':
                            check = True

            if check:
                try:
                    asset = task.getAssets(assetTypes=['comp'])[0]
                    version = asset.getVersions()[-1]
                    script = version.getComponent(name='nukescript')

                    # version up nuke script file
                    path = script.getFilesystemPath()
                    [new_path, version_number] = version_up(path)

                    # publishing version in FTrack
                    id = task.get('entityId')
                    new_version = asset.createVersion(taskid=id)
                    new_version.createComponent(name='nukescript',
                                                path=new_path)
                    new_version.publish()
                except:
                    log.error(traceback.format_exc())
                else:
                    # Get path to task
                    path = task.get('name')
                    for p in task.getParents():
                        path = p.get('name') + '/' + path

                    msg = "Version from %s" % version_number
                    msg += " to %s on %s" % ((version_number + 1), path)
                    log.info(msg)


def main(event):
    success = plugins_api.check_project(event, __file__)
    if success:
        callback(event)
