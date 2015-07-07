import os
import sys

path = os.path.dirname(__file__)
sys.path.append(path)

import server

server.setup('production_plugins')
