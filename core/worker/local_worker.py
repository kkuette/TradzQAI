from tools import *

import time
import sys
import numpy as np

from tqdm import tqdm
tqdm.monitor_interval = 0

from PyQt5.QtCore import *
# QThread

class Local_Worker(QThread):

    sig_step = pyqtSignal()
    sig_batch = pyqtSignal()
    sig_episode = pyqtSignal()

    def __init__(self, env=None, agent=None):
        self.name = os.path.basename(__file__).replace(".py", "")

        if not env or not agent:
            raise ValueError("The worker need an agent and an environnement")

        self.env = env
        self.agent = agent
        #env.logger.new_logs(self.name)
        #env.logger._add("Initialization", self.name)
        self.deterministic = False
        if "eval" in self.env.mode:
            self.env.episode_count = 1
            self.deterministic = True
        QThread.__init__(self)

    def run(self):
        step = range(self.env.dl.files_count)
        if self.env.gui == 0:
            step = tqdm(step)

        for s in step:
            if self.env.gui == 0:
                d = self.env.dl.files[s].split('/')
                step.set_description(desc="%s " % d[len(d) - 1], refresh=True)
                step.update(1)
            self.step()
            self.env.nextDataset()
            if self.env.stop:
                break

        if self.env.mode == "eval":
            self.env.eval_processing()
        step.close()
        self.env.close()

    def step(self):
        ep = range(self.env.episode_count)
        if self.env.gui == 0:
            ep = tqdm(ep, desc="Episode Processing ")

        for e in ep:
            state = self.env.reset()
            self.agent.reset()
            self.env.start_t = time.time()
            dat = range(self.env.len_data)
            if self.env.gui == 0:
                dat = tqdm(dat, desc="Step Processing ")
            for t in dat:
                tmp = time.time()
                action = self.agent.act(state, deterministic=self.deterministic) # Get action from agent
                # Get new state
                state, terminal, reward = self.env.execute(action)
                if "train" == self.env.mode:
                    self.agent.observe(reward=reward, terminal=terminal)
                if self.env.gui == 1:
                    self.sig_step.emit() # Update GUI
                    time.sleep(0.07)
                elif self.env.gui == 0:
                    dat.update(1)
                self.env.loop_t = time.time() - tmp
                if terminal or self.agent.should_stop() or self.env.stop:
                    if terminal and self.env.mode == "train":
                        self.agent.save_model(directory=self.env.saver.model_file_path, append_timestep=True)
                    break

            if self.env.gui == 0:
                dat.close()
                ep.update(1)
            elif self.env.gui == 1:
                self.sig_episode.emit()
            if e == self.env.episode_count - 1:
                self.env.next = True
            if self.agent.should_stop() or self.env.stop or self.env.next:
                ep.close()
                break
