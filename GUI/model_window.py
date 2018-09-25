import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pyqtgraph as pg

class ModelWindow(QWidget):

    def __init__(self, root, env):
        super(QWidget, self).__init__(root)
        GL = QGridLayout(self)
        tab = QTabWidget()

        tab.addTab(self.step_graph(), 'Step')
        tab.addTab(self.batch_graph(), 'Batch')
        tab.addTab(self.episode_graph(), 'Episode')

        GL.addWidget(tab, 0, 0)

    def episode_graph(self):
        QW = QWidget()
        GL = QGridLayout()

        #self.g_eloss = pg.PlotWidget()
        #self.g_eloss.setTitle('Loss')

        self.g_ereward = pg.PlotWidget()
        self.g_ereward.setTitle('Reward')

        self.g_eprofit = pg.PlotWidget()
        self.g_eprofit.setTitle('Return')

        #GL.addWidget(self.g_eloss, 0, 0)
        GL.addWidget(self.g_ereward, 1, 0)
        GL.addWidget(self.g_eprofit, 2, 0)

        QW.setLayout(GL)

        return QW

    def batch_graph(self):
        QW = QWidget()
        GL = QGridLayout()

        self.g_bloss = pg.PlotWidget()
        self.g_bloss.setTitle('Loss')

        GL.addWidget(self.g_bloss, 0, 0)

        QW.setLayout(GL)

        return QW

    def step_graph(self):
        QW = QWidget()
        GL = QGridLayout()

        self.g_act = pg.PlotWidget()
        self.g_act.setTitle('Action')

        self.g_profit = pg.PlotWidget()
        self.g_profit.setTitle('Return')

        self.g_state = pg.PlotWidget()
        self.g_state.setTitle('State')

        self.g_reward = pg.PlotWidget()
        self.g_reward.setTitle('Reward')

        GL.addWidget(self.g_state, 0, 0)
        GL.addWidget(self.g_act, 1, 0)
        GL.addWidget(self.g_reward, 2, 0)
        GL.addWidget(self.g_profit, 3, 0)

        QW.setLayout(GL)

        return QW

    def update_episode(self, env):
        #self.g_eloss.clear()
        self.g_ereward.clear()
        self.g_eprofit.clear()

        #self.g_eloss.plot(env.h_lst_loss)
        self.g_eprofit.plot(env.h_lst_profit)
        self.g_ereward.plot(env.h_lst_reward)

    def update_batch(self, env):
        self.g_bloss.clear()
        l = len(env.lst_loss)
        if l > 1000:
            self.g_bloss.plot(env.lst_loss[l-1001:l-1])
        else:
            self.g_bloss.plot(env.lst_loss)

    def update_step(self, env):
        self.g_reward.clear()
        self.g_state.clear()
        self.g_profit.clear()
        self.g_act.clear()

        self.g_reward.plot(self.env.lst_reward)
        self.g_profit.plot(self.env.lst_return)
        self.g_act.plot(self.env.lst_act)
        self.g_state.plot(self.env.lst_state)
