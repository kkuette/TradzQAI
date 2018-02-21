import keras

from keras.models import Sequential
from keras.layers import Dense, PReLU, CuDNNLSTM, Flatten, Reshape, Dropout
from keras.optimizers import Adam

import os
import time

import numpy as np
import random
from collections import deque

from .agent import Agent

class DDRQN(Agent):

    def __init__(self, state_size, env=None, is_eval=False):
        self.name = "DDRQN"
        Agent.__init__(self, state_size, env=env, is_eval=is_eval)

    def build_model(self):
        self._load_model()
        if not self.model:
            self.model = self._model()
            self.target_model = self._model()
        else:
            self.target_model = self._model()
            self.update_target_model()

    def _model(self):
        if len(self.state_size.shape) == 1:
            input = 1
        else:
            input = self.state_size.shape[1]
        model = Sequential()
        model.add(Dense(64, input_dim=input, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Reshape((1, 32)))
        model.add(CuDNNLSTM(128))
        model.add(Dense(8, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss="mse", optimizer=Adam(lr=self.learning_rate))
        return model

    def update_target_model(self):
        old = self.target_model.get_weights()
        new = self.model.get_weights()

        weights = [[self.update_rate * n + (1 - self.update_rate) * o for n, o in zip(new_w, old_w)] for new_w, old_w in zip(new, old)]
        self.target_model.set_weights(weights)
