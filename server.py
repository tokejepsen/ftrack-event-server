import os
import sys
import logging
import time
import traceback
import datetime


# setup logging
format = '%(asctime)s - %(pathname)s - [%(levelname)s]: %(message)s'
try:
    logging.basicConfig(level=logging.INFO, format=format,
                        filename='logs/%s.log' % datetime.date.today())
except:
    logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('%(pathname)s - [%(levelname)s]:\n%(message)s\n')
handler.setFormatter(formatter)
log.addHandler(handler)

# dependencies
path = os.path.dirname(__file__)
sys.path.append(path)
sys.path.append(r'K:\tools\FTrack\ftrack-api')
sys.path.append(os.path.join(path, 'watchdog', 'src'))
sys.path.append(os.path.join(path, 'pathtools'))

import ftrack
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import plugins_api

modules = {}

ftrack.setup()

def PurgePlugins(plugins_folder):
    target_module = None
    for m in modules:
        filepath = os.path.join(plugins_folder, m.replace('.', os.sep))
        filepath += '.py'
        if not os.path.isfile(filepath):
            target_module = m

    if target_module:
        ftrack.EVENT_HUB.unsubscribe(modules[target_module])
        del modules[target_module]
        log.info('Unloaded %s!' % target_module)


def RegisterPlugin(path):
    # filter out compiled python files and init files
    f = os.path.splitext(os.path.basename(path))
    if 'pyc' in f[1] or f[0] == '__init__':
        return

    module = path.replace(os.path.dirname(__file__) + os.sep, '')
    module = os.path.splitext(module)[0].replace(os.sep, '.')
    exec('import %s' % module)
    exec('reload(%s)' % module)

    # checking for topic variable
    topic = None
    try:
        exec('topic = %s.topic' % module)
    except Exception as e:
        msg = 'No "topic" variable found'
        msg += ' in %s' % path
        log.warning(msg)

    # checking for main function
    main = None
    try:
        exec('main = %s.main' % module)
    except Exception as e:
        msg = 'No "main" function found'
        msg += ' in %s' % path
        log.warning(msg)

    # subscribing plugins
    if topic and main:
        if module in modules:
            ftrack.EVENT_HUB.unsubscribe(modules[module])
            del modules[module]
            log.info('Unloaded %s!' % module)
        id = ftrack.EVENT_HUB.subscribe('topic=%s' % topic, main)
        modules[module] = id
        log.info('Loaded %s!' % module)


class MyHandler(FileSystemEventHandler):

    def __init__(self, plugins_folder):
        super(MyHandler, self).__init__()
        self.plugins_folder = plugins_folder

    def on_modified(self, event):
        if os.path.isfile(event.src_path):
            try:
                PurgePlugins(self.plugins_folder)
                RegisterPlugin(event.src_path)
            except Exception as e:
                log.error(e)

    def on_deleted(self, event):
        try:
            PurgePlugins(self.plugins_folder)
        except Exception as e:
            log.error(e)


def setup(plugins_folder):
    file_path = os.path.dirname(__file__)
    path = os.path.join(file_path, plugins_folder)
    sys.path.append(path)

    for root, dirs, files in os.walk(path):
        for f in files:
            # importing plugin
            RegisterPlugin(os.path.join(root, f))

    event_handler = MyHandler(file_path)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:

        ftrack.EVENT_HUB.wait()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
