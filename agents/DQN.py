import keras
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.optimizers import Adam

import os
import time

import numpy as np
import random
from collections import deque

from .agent import Agent

class DQN(Agent):

    def __init__(self, state_size, env=None, is_eval=False):
        self.name = "DQN"
        Agent.__init__(self, state_size, env=env, is_eval=is_eval)

    def build_model(self):
        self._load_model()
        if not self.model:
            self.model = self._model()

    def _model(self):
        if len(self.state_size.shape) == 1:
            input = 1
        else:
            input = self.state_size.shape[1]
        model = Sequential()
        model.add(Dense(64, input_dim=input, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(8, activation='relu'))
        model.add(Dense(self.action_size, activation="linear"))
        model.compile(loss="mse", optimizer=Adam(lr=self.learning_rate))
        return model
