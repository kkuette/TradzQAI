from environnement import Environnement

import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pyqtgraph as pg

class Model_Window(QWidget):

    def __init__(self, root, env):
        super(QWidget, self).__init__()
        GB = QGridLayout(self)

        self.loss_graph()
        self.reward_graph()
        self.state_graph()
        self.profit_graph()
        self.act_graph()

        GB.addWidget(self.g_loss, 0, 0)
        GB.addWidget(self.g_state, 1, 0)
        GB.addWidget(self.g_act, 2, 0)
        GB.addWidget(self.g_reward, 3, 0)
        GB.addWidget(self.g_profit, 4, 0)

    def act_graph(self):
        self.g_act = pg.PlotWidget()
        self.g_act.setTitle('Action')

    def profit_graph(self):
        self.g_profit = pg.PlotWidget()
        self.g_profit.setTitle('Profit')

    def state_graph(self):
        self.g_state = pg.PlotWidget()
        self.g_state.setTitle('State')

    def loss_graph(self):
        self.g_loss = pg.PlotWidget()
        self.g_loss.setTitle('Loss')

    def reward_graph(self):
        self.g_reward = pg.PlotWidget()
        self.g_reward.setTitle('Reward')

    def Update_graph(self, env):
        self.g_loss.clear()
        self.g_reward.clear()
        self.g_state.clear()
        self.g_profit.clear()
        self.g_act.clear()

        self.g_loss.plot(env.lst_loss)
        self.g_reward.plot(env.lst_reward)
        self.g_profit.plot(env.lst_return)
        self.g_act.plot(env.lst_act)

        self.g_state.plot(env.lst_state)
