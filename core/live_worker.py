from .worker import Worker
from environnement import Environnement
from tools import *

import time

import pandas as pd

from tqdm import tqdm

class Local_Worker(Worker):

    def __init__(self, env):
        self.env = env
        self.name = os.path.basename(__file__).replace(".py", "")
        #self.env.logger._add("", self.name)
        if self.env.gui == 0:
            self.env.init_logger()
        self.env.logger.new_logs(self.name)
        self.env.logger._add("Initialization", self.name)
        Worker.__init__(self, env)
