from tools.saver import saver

import time

from collections import deque

class logger():

    def __init__(self, env):

        self.env = env

        # Init logger

        self.path = "logs/"

        self.logs = deque(maxlen=5000)
        self.id = 0

        self.current_index = 0

        self.conf = ""

        self.logs.append(time.strftime("%Y:%m:%d %H:%M:%S") + \
                        " " + '{:010d}'.format(self.id) + " " \
                        + str("Starting logs") + "\n")
        self.id += 1
    #def init_conf(self):
    #def update_conf(self):

    def init_saver(self):
        self.saver = self.env.saver
        self._add("Saver initialized")

    def _add(self, log):
        self.logs.append(time.strftime("%Y:%m:%d %H:%M:%S") + \
            " " + '{:010d}'.format(self.id) + " " + str(log) + "\n")
        if self.saver.log_file != None:
            if self.current_index < self.id:
                while self.current_index < self.id:
                    self.saver._save(logs=self.logs[self.current_index])
                    self.current_index += 1
            else:
                self.saver._save(logs=self.logs[self.id])
                self.current_index += 1
        self.id += 1
