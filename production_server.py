import os
import sys

path = os.path.dirname(__file__)
sys.path.append(path)

import server

os.environ['LOGNAME'] = 'toke.jepsen'
server.setup('production_plugins')
