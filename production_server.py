import os
import sys

path = os.path.dirname(__file__)
sys.path.append(path)

import server

os.environ['LOGNAME'] = 'milan.kolar'
server.setup('production_plugins')
