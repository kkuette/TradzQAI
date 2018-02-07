#TODO : implement EIIE
#       3 conv 2D
#       paper : https://arxiv.org/pdf/1706.10059.pdf
#       try to replicate


import keras
from keras.models import Sequential, load_model
from keras.layers import Dense, Conv2D, Flatten
from keras.optimizers import Adam

import os
import time

import numpy as np
import random
from collections import deque

from .agent import Agent

class EIIE(Agent):

    def __init__(self, state_size, env=None, is_eval=False):
        self.name = "DQN"
        Agent.__init__(self, state_size, env=env, is_eval=is_eval)

    def build_model(self):
        self._load_model()
        if not self.model:
            self.model = self._model()

    def _model(self):
        ''' Need 3D shape
        Tensor with shape (window size, nb_features(should be one,
        can be value + indics, 3 or more (close, high, low))) '''
        
        model = Sequential()
        model.add(Conv2D(3, kernel_size=(1, 3), padding='same', activation='relu', input_shape=self.state_size.shape))
        model.add(Conv2D(2, kernel_size=(1, 48), padding='same', activation='relu'))
        model.add(Conv2D(22, kernel_size=(1, 1), padding='same', activation='relu'))
        model.add(Flatten())
        model.add(Dense(22, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss="mse", optimizers=Adam(lr=self.learning_rate))
        return model
