from tools.saver import *
from core.environnement import *
import time

class logger():

    def __init__(self, env):

        # Init saver

        self.saver = saver()

        # Init logger

        self.path = "logs/"
        self.log_file = None

        self.logs = ""
        self.id = 0

    def _start(self):
        self.saver._check(env.stock_name, self.path)
        self.saver._load()

    '''
    def start_episode(self):

    def start_day(self):

    def end_episode(self):

    def end_day(self):
    '''

    def _end(self):
        self.saver._end(self.logs)
