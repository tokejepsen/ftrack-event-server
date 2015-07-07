import os
import server
import sys

sys.path.append(os.path.dirname(__file__))

os.environ['LOGNAME'] = 'toke.jepsen'
server.setup('dev_plugins')
