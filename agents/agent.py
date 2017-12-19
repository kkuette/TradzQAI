import keras

import pandas as pd
import numpy as np
import random

from collections import deque
from environnement import Environnement

class Agent:

    def __init__(self, state_size, env=None, is_eval=False, model_name=""):
        self.state_size = state_size # normalized previous days
        self.action_size = 3 # sit, buy, sell
        self.memory = deque(maxlen=1000)
        columns = ['Price', 'POS', 'Order']
        self.inventory = pd.DataFrame(columns=columns)
        self.mode = ""
        self.model_name = model_name
        self.is_eval = is_eval

        self.env = env

        self.update_rate = 1e-1
        self.learning_rate = 1e-3
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

    def act(self, state):
        if not self.is_eval and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)

        options = self.model.predict(state)
        return np.argmax(options[0])

    def _save_model(self):
        if "" in self.env.logger.model_file_name:
            self.env.logger.model_file_path = self.env.logger.model_file_path \
                      + self.name + "_" + self.env.stock_name

        self.model.save(self.env.logger.model_file_path)

    def _load_model(self):
        self.model = self.env.logger._load()
