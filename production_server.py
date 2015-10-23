import os
import sys

path = os.path.dirname(__file__)
sys.path.append(path)

import server

plugin_path = sys.argv[1:]

if not plugin_path:
    plugin_path = os.environ['FTRACK_EVENT_SERVER_PLUGINS']

server.setup(plugin_path)
