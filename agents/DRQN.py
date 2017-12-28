import keras
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, PReLU, CuDNNLSTM, Reshape
from keras.optimizers import Adam

import os
import time

import numpy as np
import random
from collections import deque

from .agent import Agent

class DRQN(Agent):

    def __init__(self, state_size, env=None, is_eval=False, model_name=""):
        self.name = "DRQN"
        Agent.__init__(self, state_size, env=env, is_eval=is_eval, model_name=model_name)

    def build_model(self):
        self._load_model()
        if not self.model:
            self.model = self._model()

    def _model(self):
        model = Sequential()
        model.add(Dense(64, input_dim=self.state_size.shape[1], activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Reshape((1, 32)))
        model.add(CuDNNLSTM(128))
        model.add(Dense(8, activation='relu'))
        model.add(Dense(self.action_size, activation="linear"))
        model.compile(loss="mse", optimizer=Adam(lr=self.learning_rate))
        return model
