from tensorforce.agents import DDPGAgent

from collections import deque
import pandas as pd

class DDPG(DDPGAgent):

    def __init__(self, state_size, env=None, is_eval=False):
        self.state_size = state_size
        self.action_size = 3
        self.memory_size = 1000
        self.is_eval = is_eval
        self.env = env

        DDPGAgent.__init__(self,
                           states = dict(type='float', shape=self.state_size.shape),
                           actions = dict(type='int', num_actions=self.action_size),
                           network = env.get_network(),
                           critic_network = env.get_network(),
                           discount = env.hyperparameters['gamma'],
                           batching_capacity = 10000,
                           actions_exploration = env.exploration)

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
