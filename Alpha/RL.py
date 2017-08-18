from RNN import *

class RL():

    def __init__(self):
        self.actions = ['Buy', 'Hold', 'Sell']
        self.state = None
        self.Q = {}
        self.discount = 0.3
        self.alpha = 1
        self.time = 1
        self.player = 0, 1
        self.value_score = {}
        self.act_reward = -0.05

    def init_Q(self):
        for states in self.state:
            tmp = {}
            for action in self.actions:
                tmp[action] = 0.1
            self.Q[states] = tmp

