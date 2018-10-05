from .base import Environnement
from .contracts import CFD, Classic
from tools import *

import pandas as pd
import numpy as np
from collections import deque
from tqdm import tqdm

import os
import sys
import time

class Live_env(Environnement):

    def __init__(self, mode="train", gui=0, contract_type="classic",
            config=None, agent="PPO", api=None):
        Environnement.__init__(self, gui=gui)
        if "cfd" == contract_type:
            self.contracts = CFD()
        elif "classic" == contract_type:
            self.contracts = Classic()
        else:
            raise ValueError("Contract type does not exist")

        self.api = api
        if not self.api:
            raise ValueError("There is no API, we cannot launch live env")
        self.model_name = agent

        self.crypto = ['BTC', 'LTC', 'BCH', 'ETH']
        self.is_crypto = False

        self.contract_type = contract_type

        self.logger = None
        self.episode_count = 0

        self.window_size = 10
        self.t_return = 2
        self.r_period = 10

        self.mode = mode
        self._name = self.mode

        self.wallet = self.contracts.getWallet()
        self.inventory = self.contracts.getInventory()
        self.saver = Saver()
        self.settings = dict(
            network = self.get_network(),
            agent = self.get_agent_settings(),
            env = self.get_env_settings()
        )

        if self.saver.check_settings_files(config):
            self.settings['env'], self.settings['agent'], self.settings['network'] = self.saver.load_settings(config)
            self.get_settings(self.settings['env'])
        else:
            self.saver.save_settings(self.settings['env'],
                self.settings['agent'], self.settings['network'], config)

        if "cfd" == self.contract_type:
            self.contracts = CFD()
        elif "classic" == self.contract_type:
            self.contracts = Classic()
        else:
            raise ValueError("Contract type does not exist")
        self.api.start()
        acc = self.api.getAccount()
        if not 'message' in acc:
            self.settings['capital'] = acc['available']
        else:
            print ("Client not connected")
        self.dl = dataLoader(mode=self.mode, api=self.api)
        self.model_dir = self.model_name
        self.saver._check(self.model_dir, self.settings)

        self.logger = Logger()
        self.logger.setEvent(self.event)
        self.logger.set_log_path(self.saver.get_model_dir()+"/")
        self.logger.new_logs(self._name)
        self.dl.setLogger(self.logger)
        if self.mode == "eval":
            self.logger.new_logs("summary_eval")

        self.dl.loadHistorical()

        self.data, self.raw, self._date = self.dl.getData(), self.dl.getRaw(), self.dl.getTime()
        self.len_data = len(self.raw['Price'])
        self.state = getState(self.raw, self.len_data-self.window_size , self.window_size + 1)
        '''
        for crypt in self.crypto:
            if crypt in (self.dl.files[0].split("/"))[len(self.dl.files[0].split("/")) - 1].split("_"):
        '''
        self.is_crypto = True

        if self.is_crypto and 'cfd' in self.contract_type:
            self.close()
            raise ValueError("Cryptocurrencies cannot be traded as cfd.\
                \nPlease change contract type to classic.")


    def close(self):
        self.stop = True
        if self.logger:
            self.logger.stop()
        self.event.set()

    def nextData(self):
        self.dl.loadProcessedData()
        self.data, self.raw, self._date = self.dl.getData(), self.dl.getRaw(), self.dl.getTime()
        self.len_data = len(self.raw['Price'])

    def get_env_settings(self):
        self.contract_settings = self.contracts.getSettings()

        c_settings = dict(
            allow_short = self.contract_settings['allow_short'],
            contract_size = self.contract_settings['contract_size'],
            contract_price = self.contract_settings['contract_price'],
            pip_value = self.contract_settings['pip_value'],
            spread = self.contract_settings['spread']
        )

        #data_directory = self.dataDirectory,
        self.meta = dict(
            episodes = self.episode_count,
            window_size = self.window_size,
            targeted_return = self.t_return,
            data_directory = "data/",
            reward_period = self.r_period,
            contract_type = self.contract_type,
        )

        w_settings = dict(
            capital = self.wallet.settings['capital'],
            fee = self.wallet.settings['fee']
        )

        r_settings = dict(
            exposure = self.wallet.risk_managment['exposure'],
            max_pos = self.wallet.risk_managment['max_pos'],
            stop_loss = self.wallet.risk_managment['stop_loss']
        )

        env = dict(contract_settings = c_settings,
                   wallet_settings = w_settings,
                   risk_managment = r_settings,
                   env_settings = self.meta)

        return env

    def rewa(self):
        self.r_av.append(self.r_pnl[self.current_step['step']] - self.r_pnl[self.current_step['step'] - 1])
        if self.current_step['step'] > 0:
            if self.current_step['step'] > self.r_period:
                return np.average(self.r_av[self.current_step['step']-self.r_period:])
            else:
                return np.average(self.r_av)
        else:
            return 0

    def execute(self, action):
        if self.pause == 1:
            while (self.pause == 1):
                time.sleep(0.01)
        self.nextData()
        self.current_step['step'] += 1
        self.closed = False
        self.action = action

        self.reward['current'] = 0
        self.wallet.profit['current'] = 0
        if self.current_step['step'] == 0:
            self.contract_settings['contract_price'] = self.contracts.getContractPrice(self.data[self.current_step['step']])
            if self.is_crypto:
                self.contract_settings['contract_size'] = self.wallet.manage_contract_size(self.contract_settings)
        self.price['buy'], self.price['sell'] = self.contracts.calcBidnAsk(self.data[self.current_step['step']])
        self.wallet.manage_exposure(self.contract_settings)
        stopped = self.inventory.stop_loss(self)
        if not stopped:
            force_closing = self.inventory.trade_closing(self)
            if not force_closing:
                self.inventory.inventory_managment(self)
            else:
                if self.inventory.get_last_trade()['close']['pos'] == "SELL":
                    self.action = 2
                else:
                    self.action = 1
        else:
            if self.inventory.get_last_trade()['close']['pos'] == "SELL":
                self.action = 2
            else:
                self.action = 1


        self.wallet.manage_wallet(self.inventory.get_inventory(), self.price,
                            self.contract_settings)
        if self.current_step['step'] > 0:
            self.contract_settings['contract_price'] = self.contracts.getContractPrice(self.data[self.current_step['step']])
            if self.is_crypto:
                self.contract_settings['contract_size'] = self.wallet.manage_contract_size(self.contract_settings)

        #self.train_in.append(self.state)
        #self.train_out.append(act_processing(self.action))

        self.r_pnl.append(self.wallet.settings['GL_profit'])
        self.reward['current'] += round(self.rewa(), 4)
        #self.reward['current'] += (self.r_pnl[self.current_step['step']] - self.r_av[self.current_step['step']])
        self.wallet.profit['daily'] += self.wallet.profit['current']
        self.wallet.profit['total'] += self.wallet.profit['current']
        self.reward['daily'] += self.reward['current']
        self.reward['total'] += self.reward['current']
        self.lst_reward.append(self.reward['current'])
        if self.gui == 1:
            self.def_act()
            self.chart_preprocessing(self.data[self.current_step['step']])
        self.state = getState(self.raw, self.len_data-self.window_size,
                            self.window_size + 1)
        self.wallet.daily_process()
        done = False
        if self.wallet.risk_managment['current_max_pos'] < 1:
            tqdm.write(str(self.wallet.risk_managment))
            tqdm.write(str(self.wallet.settings))
            tqdm.write(str(self.contract_settings['contract_price']))
            tqdm.write(str(self.contract_settings['contract_size']))
            tqdm.write(str(self.current_step['step']))
            done = True
        return self.state, done, self.reward['current']

    def daily_reset(self):
        self.wallet.daily_reset()
        self.lst_reward = []

        self.daily_trade = dict(
            win = 0,
            loss = 0,
            draw = 0,
            total = 0
        )

        self.reward['current'] = 0
        self.reward['daily'] = 0

        self.train_in = []
        self.train_out = []

    def reset(self):
        try:
            self.h_lst_reward.append(self.reward['total'])
            self.h_lst_profit.append(self.wallet.profit['total'])
            self.h_lst_win_order.append(self.trade['win'])
            self.h_lst_loose_order.append(self.trade['loss'])
            self.h_lst_draw_order.append(self.trade['draw'])
        except:
            self.h_lst_reward = []
            self.h_lst_profit = []
            self.h_lst_win_order = []
            self.h_lst_loose_order = []
            self.h_lst_draw_order = []

        self.tensorOCHL = [[] for _ in range(4)]
        self.step_left = 0
        self.lst_reward_daily = []
        self.lst_data_full = deque(maxlen=100)
        self.date['day'] = 1
        self.date['month'] = 1
        self.date['year'] = 1
        self.date['total_minutes'] = 1
        self.date['total_day'] = 1
        self.date['total_month'] = 1
        self.date['total_year'] = 1

        self.r_pnl = []
        self.r_av = []
        self.start = 0
        self.switch = 0

        self.reward = dict(
            current = 0,
            daily = 0,
            total = 0
        )

        self.trade = dict(
            win = 0,
            loss = 0,
            draw = 0,
            total = 0,
        )

        self.price = dict(
            buy = 0,
            sell = 0
        )
        self.next = False
        self.daily_reset()
        self.wallet.reset()
        self.inventory.reset()
        self.current_step['step'] = -1
        self.new_episode = True
        self.state = getState(self.raw, 0, self.window_size + 1)
        self.current_step['episode'] += 1
        self.logger._add("Starting episode : " + str(self.current_step['episode']),
                    self._name)
        return self.state
