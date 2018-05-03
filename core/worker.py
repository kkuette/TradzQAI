from math import *

import time
import pandas as pd
import sys
import os

from environnement import Environnement
from tools import *

from PyQt5.QtCore import *

class Worker(QThread):


    sig_step = pyqtSignal()
    sig_batch = pyqtSignal()
    sig_episode = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)

    def init_agent(self, env):
        if "eval" in env.mode:
            is_eval = True
        else:
            is_eval = False

        if env.model_name in env.agents:
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore",category=FutureWarning)
                Agent = getattr(__import__("agents", fromlist=[env.model_name]), env.model_name)
        else:
            raise ValueError('could not import %s' % env.model_name)
        self.agent = Agent(env.state,
                           env=env,
                           is_eval=is_eval)

        self.agent.build_model()
        '''
        if self.env.logger.model_summary_file:
            self.env.logger.save_model_summary(self.agent.model)
        '''
