"""
Thanks to https://github.com/jdloft/multiprocess-logging/blob/master/main.py
for the logging solution.
"""

import os
import multiprocessing
import logging
import sys
import traceback


# setup environment
try:
    import config

    os.environ["FTRACK_SERVER"] = config.server_url
    os.environ["FTRACK_API_USER"] = config.user
    os.environ["LOGNAME"] = config.user
    os.environ["FTRACK_API_KEY"] = config.api_key
except ImportError:
    print("No \"config\" found.")
else:
    print(traceback.format_exc())


class StreamToLogger(object):
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""

    def write(self, buf):
        if buf != "\n":
            self.logger.log(self.log_level, buf)

    def flush(self):
        pass


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s:\n%(message)s")


class JobProcess(multiprocessing.Process):
    def __init__(self, name, path):
        super(JobProcess, self).__init__()
        self.name = name
        self.path = path

    def run(self):
        thread_logger = logging.getLogger(self.name)
        sys.stdout = StreamToLogger(thread_logger, logging.INFO)
        sys.stderr = StreamToLogger(thread_logger, logging.ERROR)
        sys.path.append(os.path.dirname(self.path))

        print("Running {}".format(self.path))

        try:
            execfile(self.path, {"__file__": self.path})
        except Exception:
            print(traceback.format_exc())


def main():

    # getting plugins
    args = sys.argv[1:]
    paths = []
    for arg in args:
        if os.path.isdir(arg):
            result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(arg)
                      for f in filenames if os.path.splitext(f)[1] == ".py"]
            paths.extend(result)

        if os.path.isfile(arg):
            paths.append(arg)

    if not paths:
        plugins = os.environ.get("FTRACK_EVENT_SERVER_PLUGINS", "")
        for path in plugins.split(os.pathsep):
            if os.path.isfile(path):
                paths.append(path)
            if os.path.isdir(path):
                for f in os.listdir(path):
                    if f.endswith(".py"):
                        paths.append(os.path.join(path, f))

    paths = list(set(paths))

    print("Plugins found: {}".format(paths))

    # starting event plugins
    for path in paths:
        t = JobProcess(path, path)
        t.start()

    while True:
        pass


if __name__ == "__main__":
    main()
