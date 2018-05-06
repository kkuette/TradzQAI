from tensorforce.agents import TRPOAgent

from collections import deque
import pandas as pd

class TRPO(TRPOAgent):

    def __init__(self, state_size, env=None, is_eval=False):
        self.state_size = state_size
        self.action_size = 3
        self._memory_size = 1000
        self._memory = deque(maxlen=1000)
        self.is_eval = is_eval
        self.env = env

        TRPOAgent.__init__(self,
                           states = dict(type='float', shape=self.state_size.shape),
                           actions = dict(type='int', num_actions=self.action_size),
                           network = env.get_network(),
                           discount = env.hyperparameters['gamma'],
                           batching_capacity = env.batch_size * 100,
                           learning_rate = env.hyperparameters['learning_rate'])

        self._load_model()

    def build_model(self):
        pass

    def expReplay(self, reward, done):
        self.observe(reward=reward, terminal=done)

    def _save_model(self):
        if self.env.logger.model_file_name == "":
            self.env.logger.model_file_name = self.env.model_name + "_" + self.env.stock_name
            self.env.logger.model_file_path = self.env.logger.model_directory + "/" + self.env.logger.model_file_name
        self.save_model(directory=self.env.logger.model_file_path, append_timestep=True)

    def _load_model(self):
        try:
            self.restore_model(self.env.logger.model_directory)
        except:
            pass
