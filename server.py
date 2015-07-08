import os
import sys
import logging
import time
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

    root, parent = os.path.split(
        os.path.abspath(os.path.join(path, os.pardir)))

    module_list = [parent, f[0]]
    module = '.'.join(module_list)
    try:
        exec('import %s' % module)
        exec('reload(%s)' % module)
    except ImportError:
        print 'module: ' + module + ' could not be imported'
        return

    # checking for topic variable
    topic = None
    try:
        exec('topic = %s.topic' % module)
    except Exception:
        msg = 'No "topic" variable found'
        msg += ' in %s' % path
        log.warning(msg)

    # checking for main function
    main = None
    try:
        exec('main = %s.main' % module)
    except Exception:
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
    # file_path = os.path.dirname(__file__)
    # path = os.path.join(file_path, plugins_folder)

    sys.path.append(plugins_folder)

    for root, dirs, files in os.walk(plugins_folder):
        for f in files:
            # importing plugin
            RegisterPlugin(os.path.join(root, f))

    event_handler = MyHandler(plugins_folder)
    observer = Observer()
    observer.schedule(event_handler, plugins_folder, recursive=True)
    observer.start()
    try:

        ftrack.EVENT_HUB.wait()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
