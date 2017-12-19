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
        model.add(Dense(32, input_dim=self.state_size.shape[1], activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Reshape((1, 32)))
        model.add(CuDNNLSTM(128))
        model.add(Dense(self.action_size, activation="linear"))
        model.compile(loss="mse", optimizer=Adam(lr=self.learning_rate))
        return model
    
    def expReplay(self, batch_size):
        mini_batch = []
        l = len(self.memory)
        for i in range(l - batch_size + 1, l):
            mini_batch.append(self.memory[i])

        for state, action, reward, next_state, done in mini_batch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(next_state)[0])

            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay 

