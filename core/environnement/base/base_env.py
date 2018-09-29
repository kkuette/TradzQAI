from tools import *
from .wallet import Wallet
from .inventory import Inventory

import pandas as pd
import numpy as np
from collections import deque
from tqdm import tqdm, trange

import os
import sys
import time

class Environnement(object):

    def __init__(self, gui):

        #self._name = os.path.basename(__file__).replace(".py", "")
        self.name = "TradzQAI"
        self.version = "v0.2"
        self.v_state = "Alpha"
        self._platform = sys.platform
        self.agents = self.src_agents()
        self.gui = gui

        self.current_step = dict(
            episode = 0,
            step = -1
        )

        self.date = dict(
            day = 1,
            month = 1,
            year = 1,
            total_minutes = 1,
            total_day = 1,
            total_month = 1,
            total_year = 1
        )

        self.actions = 3
        self.step_left = 0
        self.pause = 0
        self.action = None
        self.start_t = 0
        self.loop_t = 0
        self.mod_ordr = False
        self.day_changed = False
        self.new_episode = False
        self.closed = False

        self.lst_act = deque(maxlen=1000)
        self.lst_reward = deque(maxlen=1000)
        self.lst_state = deque(maxlen=1000)

        self.train_in = []
        self.train_out = []

        self.time = None
        self.lst_data_full = deque(maxlen=100)
        self.lst_data_preprocessed = []
        self.offset = 0

        self.historical = []

        self.tensorOCHL = [[] for _ in range(4)]

    def get_network(self):

        network = [dict(type='dense', size=64, activation='relu'),
                   dict(type='dense', size=64, activation='relu'),
                   dict(type='dense', size=64, activation='relu')]

        '''

        network = [dict(
                type = "conv1d",
                size = 32,
                window = 10,
                stride = 1,
                padding = "SAME"
            ),
            #dict(
            #    type="pool2d",
            #    pooling_type='max',
            #    window=4,
            #    stride=1,
            #    padding='SAME'
            #),
            dict(
                type = "conv1d",
                size = 32,
                window = 5,
                stride = 1,
                padding = "SAME"
            ),
            #dict(
            #    type="pool2d",
            #    pooling_type='max',
            #    window=2,
            #    stride=1,
            #    padding='SAME'
            #),
            dict(
                type = "flatten"
            ),
            dict(
                type="dense",
                size=256,
                activation="relu",
            )
        ]
        '''



        return network

    def get_settings(self, env):
        self.window_size = env['env_settings']['window_size']
        #self.model_name = env['env_settings']['agent']
        self.dataDirectory = env['env_settings']['data_directory']
        del env['env_settings']['data_directory']
        self.episode_count = env['env_settings']['episodes']
        self.t_return = env['env_settings']['targeted_return']
        self.r_period = env['env_settings']['reward_period']
        for name, value in env['contract_settings'].items():
            self.contract_settings[name] = value
        for name, value in env['wallet_settings'].items():
            self.wallet.settings[name] = value
        for name, value in env['risk_managment'].items():
            self.wallet.risk_managment[name] = value
        self.wallet.init_default()

    def _pause(self):
        self.pause = 1

    def _resume(self):
        self.pause = 0

    def def_act(self):
        if self.action == 1:
            self.act = "BUY"
            self.lst_act.append(1)
        elif self.action == 2:
            self.act = "SELL"
            self.lst_act.append(-1)
        else:
            self.act = "HOLD"
            self.lst_act.append(0)

    def manage_orders(self, ordr):
        if self.closed is True:
            last_trade = self.inventory.get_last_trade()
            new = [str(last_trade['open']['pos']) \
                   + " : " \
                   + '{:.2f}'.format(last_trade['open']['price']) \
                   + " -> " \
                   + str(last_trade['close']['pos']) \
                   + " : " \
                   + '{:.2f}'.format(last_trade['close']['price']) \
                   + " | Profit : " \
                   + '{:.5f}'.format(last_trade['profit']) \
                   + " | Fee : " \
                   + '{:.5f}'.format(last_trade['fee'])]

            if len(ordr['Orders']) > 37:
                ordr = (ordr.drop(0)).reset_index(drop=True)
            ordr = ordr.append(pd.DataFrame(new, columns = ['Orders']), ignore_index=True)
            self.mod_ordr = True
        else:
            self.mod_ordr = False
        return ordr

    def src_agents(self):
        ignore = ['Agent.py', '__init__.py', '__pycache__']
        valid = []
        for f in os.listdir("agents"):
            if f not in ignore:
                valid.append(f.replace(".py", ""))
        return valid

    def check_dates(self):
        if type(self._date[0]) == str():
            self._date = self._date.apply(lambda x: x.replace(" ", "")[:12])
        else:
            self._date = self._date.apply(lambda x: str(x))
        #if self.gui == 0:
            #ldate = tqdm(range(1, self.len_data), desc = "Checking dates ")
        #else:
        ldate = range(1, self.len_data)
        for r in ldate:
            date_c = self._date[r]
            date_p = self._date[r - 1]
            if date_p[11] != date_c[11]:
                self.date['total_minutes'] += 1
            if date_p[7] != date_c[7]:
                self.date['total_day'] += 1
            if date_p[5] != date_c[5]:
                self.date['total_month'] += 1
            if date_p[3] != date_c[3]:
                self.date['total_day'] += 1
        if self.date['total_minutes'] != len(self._date) - 1:
            self.time = "Tick"
        else:
            self.time = "1M"

    def check_time_before_closing(self):
        if self.current_step['step'] == self.len_data - 1:
            return
        for idx in range(self.current_step['step'] + 1 , self.len_data - 1):
            if self._date[idx - 1][7] != self._date[idx][7]:
                break
        self.step_left = idx - self.current_step['step'] + 1


    def manage_date(self):
        self.day_changed = False
        if self.current_step['step'] > 0:
            if self._date[self.current_step['step'] - 1][3] != self._date[self.current_step['step']][3]:
                self.date['year'] += 1
                self.date['month'] = 1
                self.date['day'] = 1
                self.day_changed = True
            elif self._date[self.current_step['step'] - 1][5] != self._date[self.current_step['step']][5]:
                self.date['month'] += 1
                self.date['day'] = 1
                self.day_changed = True
            elif self._date[self.current_step['step'] - 1][7] != self._date[self.current_step['step']][7]:
                self.date['day'] += 1
                self.day_changed = True
        if self.day_changed is True:
            return 1
        else:
            return 0

    def get3DState(self):
        for idx in range(len(self.lst_data_preprocessed)):
            self.tensorOCHL[idx].append(self.lst_data_preprocessed[idx])
        state = getState(self.raw,
                         self.current_step['step'] + 1,
                         self.window_size + 1)
        d = self.current_step['step'] - self.window_size + 1
        #tensorState = [[] for _ in range(len(self.tensorOCHL))]
        tensorState = []
        for i in range(self.window_size):
            if d+i > 0 and i > 0:
                if self._date[self.current_step['step'] - (d + i)][11] == "0" or self._date[self.current_step['step'] - (d + i) + 1][11] == "5":
                    tensorState.append([state[i], state[i], state[i], state[i]])
                    #tensorState[1].append(state[i])
                    #tensorState[2].append(state[i])
                    #tensorState[3].append(state[i])
                elif self.current_step['step'] and self.tensorOCHL[2][self.current_step['step'] - (d + i)] > self.tensorOCHL[2][self.current_step['step'] - (d + i) + 1]:
                    tensorState.append([state[i], tensorState[i - 1][1], state[i], tensorState[i - 1][3]])
                    #tensorState[0].append(state[i])
                    #tensorState[1].append(tensorState[1][i - 1])
                    #tensorState[3].append(tensorState[3][i - 1])
                elif self.current_step['step'] and self.tensorOCHL[3][self.current_step['step'] - (d + i)] < self.tensorOCHL[3][self.current_step['step'] - (d + i) + 1]:
                    tensorState.append([state[i], tensorState[i - 1][1], tensorState[i - 1][2], state[i]])
                    #tensorState[3].append(state[i])
                    #tensorState[0].append(state[i])
                    #tensorState[1].append(tensorState[1][i - 1])
                    #tensorState[2].append(tensorState[2][i - 1])
                else:
                    tensorState.append([tensorState[i - 1][0], state[i], tensorState[i - 1][2], tensorState[i - 1][3]])
                    #tensorState[0].append(tensorState[0][i - 1])
                    #tensorState[3].append(tensorState[3][i - 1])
                    #tensorState[2].append(tensorState[2][i - 1])
                    #tensorState[1].append(state[i])
            else:
                tensorState.append([state[i], state[i], state[i], state[i]])
                #tensorState[0].append(state[i])
                #tensorState[1].append(state[i])
                #tensorState[2].append(state[i])
                #tensorState[3].append(state[i])

        return np.array(tensorState)

    def reset_OCHL(self, data):
        self.lst_data_preprocessed = [data, data, data, data]
        self.lst_data_full.append((int(self.current_step['step'] - self.offset),
                                   self.lst_data_preprocessed[0], #open
                                   self.lst_data_preprocessed[1], #close
                                   self.lst_data_preprocessed[2], #min
                                   self.lst_data_preprocessed[3], #high
                                   self.lst_act[len(self.lst_act) - 1]))

    def add_OCHL(self, data):
        if self.current_step['step'] > 0:
            self.offset += 1
        if self.lst_data_preprocessed[2] > data:
            self.lst_data_preprocessed[2] = data
        if self.lst_data_preprocessed[3] < data:
            self.lst_data_preprocessed[3] = data
        self.lst_data_preprocessed[1] = data
        self.lst_data_full[len(self.lst_data_full) - 1] = (int(self.current_step['step'] - self.offset),
                                   self.lst_data_preprocessed[0], #open
                                   self.lst_data_preprocessed[1], #close
                                   self.lst_data_preprocessed[2], #min
                                   self.lst_data_preprocessed[3], #high
                                   self.lst_act[len(self.lst_act) - 1])

    def chart_preprocessing(self, data):
        if self.current_step['step'] == 0:
            self.reset_OCHL(data)
        elif self.time == "Tick":
            if self._date[self.current_step['step'] - 1][11] != self._date[self.current_step['step']][11]:
                self.reset_OCHL(data)
            else:
                self.add_OCHL(data)

        elif self.time == "1M":
            if self._date[self.current_step['step']][11] == "0" or self._date[self.current_step['step']][11] == "5":
                self.reset_OCHL(data)
            else:
                self.add_OCHL(data)

    def daily_processing(self, terminal):
        if self.manage_date() == 1 or terminal is True:
            self.lst_reward_daily.append(self.reward['daily'])
            self.wallet.episode_process()
            '''
            self.logger._add("Daily reward : " + str(self.reward['daily']), self._name)
            self.logger._add("Daily average rewards : " + str(self.avg_reward(env.lst_reward, 0)), self._name)
            self.logger._add("Daily profit : " + str(self.wallet.profit['daily']), self._name)
            self.logger._add("Daily trade : " + str(self.daily_trade['loss'] + self.daily_trade['win'] + self.daily_trade['draw']), self._name)
            if self.daily_trade['win'] + self.daily_trade['loss'] > 1:
                self.logger._add("Daily W/L : " + str('{:.3f}'.format(self.daily_trade['win'] / (self.daily_trade['loss'] + self.daily_trade['win']))), self._name)
            else:
                self.logger._add("Daily W/L : " + str('{:.3f}'.format(self.daily_trade['win'] / 1)), self._name)

            if self.wallet.profit['daily'] > 0:

                self.logger._add("Saving training data with " +
                                str(self.wallet.profit['daily']) +
                                " daily profit", self._name)

                self.logger.save_training_data(self.train_in,
                                              self.train_out)
            '''
            self.daily_reset()

    def avg_reward(self, reward, n):
        if n == 0:
            return np.average(np.array(reward))
        return np.average(np.array(reward[(len(reward) - 1) - n:]))

    def eval_processing(self):
        win = 0
        loss = 0
        avg_profit = 0
        avg_trade = 0
        avg_max_drawdown = 0
        avg_max_return = 0
        avg_trade_WL = 0
        for data in self.historical:
            for key, value in data.items():
                if key == 'total_profit' and value > 0:
                    win += 1
                elif key == 'total_profit' and value < 0:
                    loss += 1
                if key == 'total_profit':
                    avg_profit += value
                if key == 'total_trade':
                    avg_trade += value
                if key == 'max_drawdown':
                    avg_max_drawdown += value
                if key == 'max_return':
                    avg_max_return += value
                if key == 'trade_WL':
                    avg_trade_WL += value
        h_len = len(self.historical)
        if h_len == 0:
            return
        avg_profit /= h_len
        avg_trade /= h_len
        avg_trade_WL /= h_len
        avg_max_return /= h_len
        avg_max_drawdown /= h_len
        avg_percent_return = avg_profit / self.wallet.settings['saved_capital'] * 100
        self.logger._add("Average profit : " + str(round(avg_profit, 2)), "summary_eval")
        self.logger._add("Average max return : " + str(round(avg_max_return, 3)), "summary_eval")
        self.logger._add("Average max drawdown : " + str(round(avg_max_drawdown, 3)), "summary_eval")
        self.logger._add("Average trade : " + str(round(avg_trade, 2)), "summary_eval")
        self.logger._add("Average trade W/L : " + str(round(avg_trade_WL, 3)), "summary_eval")
        self.logger._add("Average percent return : " + str(round(avg_percent_return, 3)), "summary_eval")

        if loss + win > 0:
            self.logger._add("Day W/L : " + str(round(win / (loss + win), 3)), "summary_eval")
        else:
            self.logger._add("Day W/L : " + str(round(win / 1, 3)), "summary_eval")
        self.logger._add("Total day : " + str(h_len), "summary_eval")

    def episode_process(self):
        self.wallet.historic_process()

        h_tmp = dict(
            total_profit = round(self.wallet.profit['total'], 3),
            total_trade = self.trade['loss'] + self.trade['win'] + self.trade['draw'],
            sharp_ratio = self.wallet.historic['sharp_ratio'][self.current_step['episode'] - 1],
            mean_return = self.wallet.historic['mean_return'][self.current_step['episode'] - 1],
            max_drawdown = self.wallet.historic['max_drawdown'][self.current_step['episode'] - 1],
            max_return = self.wallet.historic['max_return'][self.current_step['episode'] - 1],
            percent_return = self.wallet.profit['percent'],
            trade_WL = 0
        )

        self.logger._add("######################################################", self._name)
        self.logger._add("Total reward : " + str(round(self.reward['total'], 3)), self._name)
        self.logger._add("Average daily reward : " + str('{:.3f}'.format(self.avg_reward(self.lst_reward_daily, 0))), self._name)
        self.logger._add("Total profit : " + str(round(self.wallet.profit['total'], 3)), self._name)
        self.logger._add("Total trade : " + str(self.trade['loss'] + self.trade['win'] + self.trade['draw']), self._name)
        self.logger._add("Sharp ratio : " + str('{:.3f}'.format(self.wallet.historic['sharp_ratio'][self.current_step['episode'] - 1])), self._name)
        self.logger._add("Mean return : " + str('{:.3f}'.format(self.wallet.historic['mean_return'][self.current_step['episode'] - 1])), self._name)
        self.logger._add("Max Drawdown : " + str('{:.3f}'.format(self.wallet.historic['max_drawdown'][self.current_step['episode'] - 1])), self._name)
        self.logger._add("Max return : " + str('{:.3f}'.format(self.wallet.historic['max_return'][self.current_step['episode'] - 1])), self._name)
        self.logger._add("Percent return : " + str('{:.3f}'.format(self.wallet.profit['percent'])), self._name)
        if  self.trade['win'] + self.trade['loss'] > 0:
            self.logger._add("Trade W/L : " + str('{:.3f}'.format(self.trade['win'] / (self.trade['loss'] + self.trade['win']))), self._name)
            h_tmp['trade_WL'] = self.trade['win'] / (self.trade['loss'] + self.trade['win'])
        else:
            self.logger._add("Trade W/L : " + str('{:.3f}'.format(self.trade['win'] / 1)), self._name)
            h_tmp['trade_WL'] = self.trade['win'] / 1
        self.logger._add("Step : " + str(self.current_step['step']), self._name)
        self.logger._add("######################################################", self._name)
        self.historical.append(h_tmp)
