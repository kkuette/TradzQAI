import keras
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, PReLU, CuDNNLSTM, Flatten, Reshape, Dropout
from keras.optimizers import Adam

import os
import time

import numpy as np
import random
from collections import deque

from core.environnement import *
from agents.agent import Agent

class DQN(Agent):

    def __init__(self, state_size):
        Agent.__init__(self, state_size, model_name=__name__)
        self.model = self._model()
        print (self.model.summary())

    def _model(self):
        model = Sequential()
        model.add(Dense(32, input_shape=(2,), activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(self.action_size, activation="linear"))
        model.compile(loss="mse", optimizer=Adam(lr=0.001))
        return model
