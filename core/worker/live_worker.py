from tools import *

import time
import sys
import json
from datetime import datetime

from threading import Thread

from tqdm import tqdm
tqdm.monitor_interval = 0

from PyQt5.QtCore import *

class Live_Worker(QThread):

    sig_step = pyqtSignal()
    sig_batch = pyqtSignal()
    sig_episode = pyqtSignal()

    def __init__(self, env=None, agent=None):
        self.name = os.path.basename(__file__).replace(".py", "")

        if env == None or agent == None:
            raise ValueError("The worker need an agent and an environnement")

        self.env = env
        self.agent = agent
        self.deterministic = False
        if "eval" == self.env.mode:
            self.determinitic = True
        self.is_working = False

        QThread.__init__(self)

    def close(self):
        self.is_working = False

    def run(self):
        self.agent.reset()
        state = self.env.reset()
        self.is_working = True
        current_time = datetime.now().minute
        current_day = datetime.now().day
        while self.is_working:
            if current_time != datetime.now().minute:
                current_time = datetime.now().minute
                action = self.agent.act(state, deterministic=self.deterministic)
                state, terminal, reward = self.env.execute(action)
                if datetime.now().day != current_day:
                    terminal = True
                    self.env.episode_process()
                if "train" == self.env.mode:
                    self.agent.observe(reward=reward, terminal=terminal)
                if self.env.gui == 1:
                    self.sig_step.emit() # Update GUI
                if terminal and self.env.mode == "train":
                    self.agent.save_model(directory=self.env.saver.model_file_path,
                        append_timestep=True)
                if terminal:
                    self.agent.reset()
                    state = self.env.reset()
                if self.agent.should_stop() or self.env.stop:
                    break

        if self.env.gui == 1:
            self.sig_episode.emit()
