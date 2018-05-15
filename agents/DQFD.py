from tensorforce.agents import DQFDAgent

from collections import deque
import pandas as pd

class DQFD(DQFDAgent):

    def __init__(self, env=None, device=None):
        self.action_size = 3
        self.env = env

        DQFDAgent.__init__(self,
                           states = dict(type='float', shape=env.state.shape),
                           actions = dict(type='int', num_actions=self.action_size),
                           network = env.settings['network'],
                           device = device,
                           discount = env.hyperparameters['gamma'],
                           batching_capacity = env.batch_size * 100,
                           learning_rate = env.hyperparameters['learning_rate'])

        self._load_model()

    def _save_model(self):
        if self.env.saver.model_file_name == "":
            try:
                self.env.saver.model_file_name = self.env.model_name + "_" + self.env.stock_name.split("_")[0] + "_" + self.env.stock_name.split("_")[1]
            except:
                self.env.saver.model_file_name = self.env.model_name + "_" + self.env.stock_name.split("_")[0]
            self.env.saver.model_file_path = self.env.saver.model_directory + "/" + self.env.saver.model_file_name
        self.save_model(directory=self.env.saver.model_file_path, append_timestep=True)

    def _load_model(self):
        try:
            self.restore_model(self.env.logger.model_direct)
        except:
            pass
