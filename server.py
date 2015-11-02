import os
import threading
import logging
import sys
import ctypes
import argparse


class LoggerWriter:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message != '\n':
            self.logger.log(self.level, message)


def _async_raise(tid, excobj):
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid,
                                                    ctypes.py_object(excobj))
    if res == 0:
        raise ValueError("nonexistent thread id")
    elif res > 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class EventThread(threading.Thread):

    def __init__(self, path):
        threading.Thread.__init__(self)

        self.path = path

    def run(self):

        with open(self.path) as f:
            content = f.read()
            exec(content)

    def raise_exc(self, excobj):
        assert self.isAlive(), "thread must be started"
        for tid, tobj in threading._active.items():
            if tobj is self:
                _async_raise(tid, excobj)
                return

        # the thread was alive when we entered the loop, but was not found
        # in the dict, hence it must have been already terminated. should we raise
        # an exception here? silently ignore?

    def terminate(self):
        # must raise the SystemExit type, instead of a SystemExit() instance
        # due to a bug in PyThreadState_SetAsyncExc
        self.raise_exc(SystemExit)


def main():

    # setup logging
    format = '%(asctime)s - %(pathname)s:\n%(message)s'
    logging.basicConfig(level=logging.INFO, format=format)
    sys.stdout = LoggerWriter(logging.getLogger(), logging.INFO)

    # getting plugins
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", action="append")

    data = parser.parse_args(sys.argv[1:])
    paths = []
    for arg in data.path:
        if os.path.isdir(arg):
            result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(arg)
                        for f in filenames if os.path.splitext(f)[1] == '.py']
            paths.extend(result)

        if os.path.isfile(arg):
            paths.append(arg)

    if not paths:
        path = os.environ['FTRACK_EVENT_SERVER_PLUGINS']
        paths = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path)
                    for f in filenames if os.path.splitext(f)[1] == '.py']

    paths = list(set(paths))

    # starting event plugins
    threads = {}
    for path in paths:
        t = EventThread(path)
        t.start()
        threads[path] = t


if __name__ == '__main__':
    main()
