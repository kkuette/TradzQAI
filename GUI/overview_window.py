from tools import *

import time

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pandas as pd
import numpy as np

class OverviewWindow(QWidget):

    def __init__(self, root, env):
        super(QWidget, self).__init__(root)

        self.ordr = pd.DataFrame(columns=['Orders'])
        self.dailyp = 0
        self.daily_reward = 0
        self.tot_reward = 0
        self.dday = 1
        self.lt = 0

        GB = QGridLayout(self)

        GB.addWidget(self.Agent_Inventory_Init(env), 0, 2, 2, 1)
        GB.addWidget(self.Agent_Orders_Init(), 0, 1)
        GB.addWidget(self.Agent_Value_Init(env), 0, 0, 2, 1)
        GB.addWidget(self.Data_Init(), 1, 1)

    def Agent_env(self, env):

        GBox = QGroupBox("Environnement")
        VBox = QVBoxLayout()

        self.lmode = QLabel('Mode : ' + env.mode)
        self.lmodel = QLabel('Model : ' + env.dataDirectory)
        self.lmax_order = QLabel('Max pos : ' + str(env.wallet.risk_managment['max_pos']))
        self.lcontract_price = QLabel('Contract price : ' + str(env.contract_settings['contract_price']))
        self.lpip_value = QLabel('Pip Value : ' + str(env.contract_settings['pip_value']))
        self.lspread = QLabel('Spread : ' + str(env.contract_settings['spread']))

        VBox.addWidget(self.lmode)
        VBox.addWidget(self.lmodel)
        VBox.addWidget(self.lmax_order)
        VBox.addWidget(self.lcontract_price)
        VBox.addWidget(self.lpip_value)
        VBox.addWidget(self.lspread)

        VBox.addStretch(1)

        GBox.setLayout(VBox)
        GBox.setFixedSize(220,180)
        return GBox

    def Agent_Inventory_Init(self, env):

        GBox = QGroupBox("Agent inventory")
        VBox = QVBoxLayout()

        self.linventory = QLabel('Empty inventory')

        self.linventory.setAlignment(Qt.AlignHCenter)

        VBox.addWidget(self.linventory)
        VBox.addWidget(self.Agent_Winrate())

        #VBox.addStretch()
        h = 245
        w = 900
        '''
        if env._platform == 'win32':
            w = 900
        if env._platform == 'Linux':
            w = 915
        '''
        GBox.setLayout(VBox)
        GBox.setFixedSize(h,w)

        return GBox

    def Agent_Orders_Init(self):

        GBox = QGroupBox("Agent orders")
        VBox = QVBoxLayout()

        self.Llist = QListWidget()

        self.l = []

        for i in range(38):
            if i < 1:
                orderi = QLabel('No orders taken yet')
            else:
                orderi = QLabel()

            orderi.setAlignment(Qt.AlignCenter)

            VBox.addWidget(orderi)

            self.l.append(orderi)

        VBox.addStretch(1)

        GBox.setLayout(VBox)
        GBox.setFixedSize(1250,775)

        return GBox

    def Data_Init(self):

        GBox = QGroupBox("Data")
        VBox = QVBoxLayout()

        self.lday = QLabel('Day : 0 / 0')
        self.lperc = QLabel('0 %')
        self.ldata = QLabel('Data : 0 / 0')
        self.lep = QLabel('Episode : 0 / 0')

        self.lperc.setAlignment(Qt.AlignCenter)
        self.lday.setAlignment(Qt.AlignCenter)
        self.ldata.setAlignment(Qt.AlignCenter)
        self.lep.setAlignment(Qt.AlignCenter)

        VBox.addWidget(self.lperc)
        VBox.addWidget(self.lday)
        VBox.addWidget(self.ldata)
        VBox.addWidget(self.lep)

        VBox.addStretch()

        GBox.setLayout(VBox)
        GBox.setFixedSize(1250,115)
        GBox.setAlignment(Qt.AlignCenter)

        return GBox

    def Agent_Winrate(self):

        GBox = QGroupBox("Winrate")
        VBox = QVBoxLayout()

        self.lwin = QLabel('Win : 0')
        self.lloose = QLabel('Loose : 0')
        self.ldraw = QLabel('Draw : 0')
        self.ltoto = QLabel('Total : 0')
        self.lwinrate = QLabel('Winrate : 0')

        VBox.addWidget(self.lwin)
        VBox.addWidget(self.lloose)
        VBox.addWidget(self.ldraw)
        VBox.addWidget(self.ltoto)
        VBox.addWidget(self.lwinrate)

        VBox.addStretch()

        GBox.setLayout(VBox)
        GBox.setFixedSize(220,155)

        return GBox

    def Agent_Value_Init(self, env):

        GBox = QGroupBox("Agent value")
        VBox = QVBoxLayout()

        self.lact = QLabel('Action : None')

        self.lact.setAlignment(Qt.AlignHCenter)

        VBox.addWidget(self.lact)
        VBox.addWidget(self.Agent_env(env))
        VBox.addWidget(self.Agent_Wallet(env))
        VBox.addWidget(self.Agent_Profit())
        VBox.addWidget(self.Agent_Reward())
        VBox.addWidget(self.Time_Init())

        VBox.addStretch()

        GBox.setLayout(VBox)

        h = 245
        if env._platform == 'win32':
            w = 900
        if env._platform == 'Linux':
            w = 915

        GBox.setFixedSize(h,w)

        return GBox

    def Agent_Wallet(self, env):

        GBox = QGroupBox("Wallet")
        VBox = QVBoxLayout()

        self.lcap = QLabel('Capital : ' + formatPrice(env.wallet.settings['capital']))
        self.lcgl = QLabel('Current G/L : ' + formatPrice(env.wallet.settings['GL_profit']))
        self.lusable_margin = QLabel('Usable margin : ' + formatPrice(env.wallet.settings['usable_margin']))
        self.lused_margin = QLabel('Used margin : ' + formatPrice(env.wallet.settings['used_margin']))

        VBox.addWidget(self.lcap)
        VBox.addWidget(self.lcgl)
        VBox.addWidget(self.lusable_margin)
        VBox.addWidget(self.lused_margin)

        VBox.addStretch()

        GBox.setLayout(VBox)
        GBox.setFixedSize(220,130)

        return GBox

    def Agent_Profit(self):

        GBox = QGroupBox("Profit")
        VBox = QVBoxLayout()

        self.lcurp = QLabel('Current : 0')
        self.ldailyp = QLabel('Daily : 0')
        self.ltotp = QLabel('Total : 0')

        VBox.addWidget(self.lcurp)
        VBox.addWidget(self.ldailyp)
        VBox.addWidget(self.ltotp)

        VBox.addStretch()

        GBox.setLayout(VBox)
        GBox.setFixedSize(220,100)

        return GBox

    def Agent_Reward(self):

        GBox = QGroupBox("Reward")
        VBox = QVBoxLayout()

        self.lcurr = QLabel('Current : 0')
        self.ldailyr = QLabel('Daily : 0')
        self.ltotr = QLabel('Total : 0')

        VBox.addWidget(self.lcurr)
        VBox.addWidget(self.ldailyr)
        VBox.addWidget(self.ltotr)

        VBox.addStretch()

        GBox.setLayout(VBox)
        GBox.setFixedSize(220,100)

        return GBox

    def Time_Init(self):

        GBox = QGroupBox("Time")
        VBox = QVBoxLayout()

        self.lstart_t = QLabel('Since start : ' + time.strftime("%H:%M:%S", time.gmtime(0)))
        self.lloop_t = QLabel('Loop : 0 ms')
        self.leta = QLabel('ETA : ' + time.strftime("%H:%M:%S", time.gmtime(0)))

        VBox.addWidget(self.lstart_t)
        VBox.addWidget(self.lloop_t)
        VBox.addWidget(self.leta)

        VBox.addStretch()

        GBox.setLayout(VBox)
        GBox.setFixedSize(220,100)

        return GBox

    def Update_Overview(self, env):

        # Episode reset

        if env.new_episode is True:
            self.lt = 0
            env.new_episode = False

        #Agent Values

        self.lact.setText('Action : ' + str(env.act))

        #Inventory

        if len(env.inventory.get_inventory()['Price']) < 1:
            self.linventory.setText('Empty inventory')
        else:
            self.linventory.setText(str(env.inventory.get_inventory()))

        #Orders Done

        if env.mod_ordr is True:
            for i in range(len(np.array(self.ordr))):
                if "Profit : -" in str(np.array(self.ordr)[i]):
                    self.l[i].setStyleSheet("QLabel {color: red}")
                elif float(str(np.array(self.ordr)[i]).split(" ")[10]) == 0:
                    self.l[i].setStyleSheet("QLabel {color: white}")
                else:
                    self.l[i].setStyleSheet("QLabel {color: green}")
                self.l[i].setText(str(np.array(self.ordr)[i]))

        #Orders

        self.lwin.setText("Win : " + str(env.trade['win']))
        self.lloose.setText("Loose : " + str(env.trade['loss']))
        self.ldraw.setText("Draw : " + str(env.trade['draw']))
        self.ltoto.setText("Total : " + str (env.trade['loss'] + env.trade['win'] + env.trade['draw']))
        if env.trade['loss'] == 0:
            self.lwinrate.setText("Winrate : " + str(1))
        else:
            self.lwinrate.setText("Winrate : " + '{:.3f}'.format(env.trade['win'] / (env.trade['loss'] + env.trade['win'])))

        #Data

        self.lep.setText("Episode : " + str(env.current_step['episode']) + " / " + str(env.episode_count))
        self.lday.setText("Day : " + str(env.date['day']) + " / " + str(env.date['total_day']))
        self.ldata.setText("Current : " +str(env.current_step['step'])+ " / " +str(len(env.data) - 1))
        self.lperc.setText('{:.2f}'.format(float((env.current_step['step'] * 100 ) / len(env.data - 1))) + " %")

        #Wallet

        self.lcap.setText('Capital : ' + formatPrice(env.wallet.settings['capital']))
        self.lcgl.setText('Current G/L : ' + formatPrice(env.wallet.settings['GL_profit']))
        self.lusable_margin.setText('Usable margin : ' + formatPrice(env.wallet.settings['usable_margin']))
        self.lused_margin.setText('Used margin : ' + formatPrice(env.wallet.settings['used_margin']))

        #Profit

        self.lcurp.setText("Current : " + formatPrice(env.wallet.profit['current']))
        self.ldailyp.setText("Daily : " + formatPrice(env.wallet.profit['daily']))
        self.ltotp.setText("Total : " + formatPrice(env.wallet.profit['total']))

        #Reward

        self.lcurr.setText("Current : " + str(env.reward['current']))
        self.ldailyr.setText("Daily : " + str(env.reward['daily']))
        self.ltotr.setText("Total : " + str(env.reward['total']))

        #Time

        now = time.time() - env.start_t
        self.lstart_t.setText("Since start : " + '{:3d}'.format(int(time.strftime("%d", time.gmtime(now))) - 1) + ":" + time.strftime("%H:%M:%S", time.gmtime(now)))
        self.lloop_t.setText("Loop : " + str(round((env.loop_t * 100), 3)) + " ms")

        if env.current_step['step'] > 0 :
            self.lt += env.loop_t
            self.leta.setText("ETA : " + '{:3d}'.format(int(time.strftime("%d", time.gmtime(((self.lt / env.current_step['step'] ) * ((len(env.data) - 1) - env.current_step['step']))))) - 1) + ":" + time.strftime("%H:%M:%S", time.gmtime((self.lt / env.current_step['step']) * ((len(env.data) - 1) - env.current_step['step']))))
        else:
            self.leta.setText("ETA : " + '{:3d}'.format(int(time.strftime("%d", time.gmtime((self.lt / 1 ) * (len(env.data) - 1)))) - 1) + ":" + time.strftime("%H:%M:%S", time.gmtime((self.lt / 1) * (len(env.data) - 1))))
