from tensorforce.agents import NAFAgent

from collections import deque
import pandas as pd

class NAF(NAFAgent):

    def __init__(self, env=None, device=None):
        self.action_size = 3
        self.env = env

        NAFAgent.__init__(self,
                           states=dict(type='float', shape=env.state.shape),
                           actions=dict(type='int', num_actions=self.action_size),
                           network=env.get_network(),
                           device=device,
                           batching_capacity=env.batch_size * 100,
                           learning_rate=env.hyperparameters['learning_rate'],
                           discount=env.hyperparameters['gamma'])

        self._load_model()

    def _save_model(self):
        if self.env.logger.model_file_name == "":
            self.env.logger.model_file_name = self.env.model_name + "_" + self.env.stock_name
            self.env.logger.model_file_path += self.env.logger.model_file_name
        self.save_model(directory=self.env.logger.model_file_path, append_timestep=True)

    def _load_model(self):
        try:
            self.restore_model(self.env.logger.model_direct)
        except:
            pass