import pandas as pd
import numpy as np
from collections import deque
from tqdm import tqdm, trange

import os
import sys
import time
from threading import Event

class Environnement:

    def __init__(self):

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
        self.api = None
        self.pause = 0
        self.action = None
        self.start_t = 0
        self.loop_t = 0
        self._api = False
        self.day_changed = False
        self.closed = False
        self.stop = False
        self.event = Event()
        self.event.clear()

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
        self.input_names = []

        self.tensorOCHL = [[] for _ in range(4)]

    def get_input_names(self, network):
        ignore = []
        if network:
            for block in network:
                if isinstance(block, list):
                    for i in block:
                        for key, value in i.items():
                            if 'names' in key:
                                for v in value:
                                    self.input_names.append(v)
                            elif 'name' in key:
                                for v in value:
                                    ignore.append(value)
                else:
                    for key, value in block.items():
                        if 'names' in key:
                            for v in value:
                                self.input_names.append(v)
                        elif 'name' in key:
                            for v in value:
                                ignore.append(value)
        for v in ignore:
            while v in self.input_names:
                for i in range(len(self.input_names)):
                    if v == self.input_names[i]:
                        self.input_names.pop(i)
                        break

    def get_network(self):
        network = [
                dict(type='dense', size=64, activation="relu"),
                dict(type='dense', size=32, activation="relu"),
                dict(type='dense', size=8, activation="relu"),
            ]
        return network

    def get_settings(self, env):
        env['base'].pop('data_directory')
        self.episode_count = env['base']['episodes']
        self.t_return = env['base']['targeted_return']
        self.contract_type = env['contract']['contract_type']
        for name, value in env['contract'].items():
            self.contract_settings[name] = value
        for name, value in env['wallet'].items():
            self.wallet.settings[name] = value
        for name, value in env['risk_managment'].items():
            self.wallet.risk_managment[name] = value
        self.wallet.init_default()

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

    def check_dates(self):
        if type(self._date[0]) == str():
            self._date = self._date.apply(lambda x: x.replace(" ", "")[:12])
        else:
            self._date = self._date.apply(lambda x: str(x))
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
            self.wallet.episode_process()
            if self.wallet.pnl['percent'] > self.t_return and (self.inventory.trades.loose + self.inventory.trades.win + self.inventory.trades.draw) > 10:
                with open("training_data/train_in.txt", "a") as f:
                    for dd in self.train_in:
                        f.write(str([[v for v in d] for d in dd])+'\n')
                with open("training_data/train_out.txt", "a") as f:
                    for row in self.train_out:
                        f.write(str(row)+'\n')
            self.daily_reset()

    def avg_reward(self, reward, n):
        if n == 0:
            return np.average(np.array(reward))
        return np.average(np.array(reward[-n:]))

    def eval_processing(self):
        self.event.set()
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
        self.event.clear()

    def episode_process(self):
        self.event.set()
        self.wallet.historic_process()

        h_tmp = dict(
            total_profit = round(self.wallet.pnl['total'], 3),
            total_trade = self.inventory.trades.loose + self.inventory.trades.win + self.inventory.trades.draw,
            sharp_ratio = self.wallet.historic['sharp_ratio'][self.current_step['episode'] - 1],
            mean_return = self.wallet.historic['mean_return'][self.current_step['episode'] - 1],
            max_drawdown = self.wallet.historic['max_drawdown'][self.current_step['episode'] - 1],
            max_return = self.wallet.historic['max_return'][self.current_step['episode'] - 1],
            percent_return = self.wallet.pnl['percent'],
            trade_WL = 0
        )

        self.logger._add("######################################################", self._name)
        self.logger._add("Total reward : " + str(round(np.sum(self.reward.total), 3)), self._name)
        self.logger._add("Average daily reward : " + str('{:.3f}'.format(self.avg_reward(self.reward.total, 0))), self._name)
        self.logger._add("Total profit : " + str(round(self.wallet.pnl['total'], 3)), self._name)
        self.logger._add("Total trade : " + str(self.inventory.trades.loose + self.inventory.trades.win + self.inventory.trades.draw), self._name)
        '''
        if len(self.inventory.pos_duration) == 0:
            self.inventory.pos_duration.append(0)
        self.logger._add("Average trade time : " + str(round(np.average(np.array(self.inventory.pos_duration)), 2)), self._name)
        self.logger._add("Max trade time : " + str(np.amax(np.array(self.inventory.pos_duration))), self._name)
        self.logger._add("Min trade time : " + str(np.amin(np.array(self.inventory.pos_duration))),self._name)
        if len(self.pos_delay['all']) == 0:
            self.pos_delay['all'].append(0)
        self.logger._add("Average trade delay : " + str(round(np.average(np.array(self.pos_delay['all'])), 2)), self._name)
        self.logger._add("Max trade delay : " + str(np.amax(np.array(self.pos_delay['all']))),self._name)
        self.logger._add("Min trade delay : " + str(np.amin(np.array(self.pos_delay['all']))),self._name)
        '''
        self.logger._add("Sharp ratio : " + str('{:.3f}'.format(self.wallet.historic['sharp_ratio'][self.current_step['episode'] - 1])), self._name)
        self.logger._add("Mean return : " + str('{:.3f}'.format(self.wallet.historic['mean_return'][self.current_step['episode'] - 1])), self._name)
        self.logger._add("Max Drawdown : " + str('{:.3f}'.format(self.wallet.historic['max_drawdown'][self.current_step['episode'] - 1])), self._name)
        self.logger._add("Max return : " + str('{:.3f}'.format(self.wallet.historic['max_return'][self.current_step['episode'] - 1])), self._name)
        self.logger._add("Percent return : " + str('{:.3f}'.format(self.wallet.pnl['percent'])), self._name)
        if  self.inventory.trades.win + self.inventory.trades.loose > 0:
            self.logger._add("Trade W/L : " + str('{:.3f}'.format(self.inventory.trades.win / (self.inventory.trades.loose + self.inventory.trades.win))), self._name)
            h_tmp['trade_WL'] = self.inventory.trades.win / (self.inventory.trades.loose + self.inventory.trades.win)
        else:
            self.logger._add("Trade W/L : " + str('{:.3f}'.format(self.inventory.trades.win / 1)), self._name)
            h_tmp['trade_WL'] = self.inventory.trades.win / 1
        self.logger._add("Step : " + str(self.current_step['step']), self._name)
        self.logger._add("######################################################", self._name)
        self.historical.append(h_tmp)
        self.event.clear()
