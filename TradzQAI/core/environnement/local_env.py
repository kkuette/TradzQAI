from TradzQAI.tools import act_processing

from .base import Environnement, Reward, Inventory, state
from .contracts import CFD, Classic

import pandas as pd
import numpy as np
from collections import deque
from tqdm import tqdm
from threading import Event

import os, sys, time, json

class Local_env(Environnement):

    def __init__(self, mode="train", contract_type="classic",
            config=None, agent="PPO", logger=None, saver=None,
            dataloader=None):

        Environnement.__init__(self)
        if "cfd" == contract_type:
            self.contracts = CFD()
        elif "classic" == contract_type:
            self.contracts = Classic()

        self.crypto = ['BTC', 'LTC', 'BCH', 'ETH']
        self.is_crypto = False

        self.settings = config

        self.contract_type = contract_type

        self.logger = logger
        self.saver = saver
        self.dl = dataloader

        self.episode_count = 1
        self.t_return = 2

        self.mode = mode
        self._name = self.mode

        self.wallet = self.contracts.getWallet()
        self.contract_settings = self.contracts.getSettings()
        
        self.price = dict(
            buy = 0,
            sell = 0
        )

        if self.dl:
            self.get_settings(config['env'])
            if "cfd" == self.contract_type:
                self.contracts = CFD()
            elif "classic" == self.contract_type:
                self.contracts = Classic()
            else:
                raise ValueError("Contract type does not exist")
            self.get_input_names(config['network'])
            if len(self.input_names) == 0:
                self.input_names = None

            self.model_name = config['agent']['type'].split('_')[0].upper()
            self.model_dir = self.model_name

            self.reward = Reward(type=config['env']['reward']['type'],
                no_neg=config['env']['reward']['no_negative'],
                period=config['env']['reward']['period'])

            self.inventory = Inventory(wallet=self.wallet, price=self.price,
                reward=self.reward, contract_settings=self.contract_settings)

            self._state = state(config['env']['states']['window'],
                preprocessing=config['env']['states']['preprocessing'],
                valid_columns=self.input_names)

            self.logger.setEvent(self.event)
            self.logger.set_log_path(self.saver.get_model_dir()+"/")
            self.logger.new_logs(self._name)
            self.dl.setLogger(self.logger)
            if self.mode == "eval":
                self.logger.new_logs("summary_eval")

            self.dl.loadFile()

            self.data, self.raw, self._date = self.dl.getData(), self.dl.getRaw(), self.dl.getTime()
            self.state = self._state(self.raw)
            if config['agent']['type'] == 'DEEP':
                self.state = np.array([self.state.ravel()])
            if self.input_names:
                self.states = dict()
                for key, value in self.state.items():
                    self.states[key] = dict(type="float", shape=value.shape)
            else:
                self.states = dict(type='float', shape=self.state.shape)
            for crypt in self.crypto:
                if crypt in (self.dl.files[0].split("/"))[len(self.dl.files[0].split("/")) - 1].split("_"):
                    self.is_crypto = True

            if self.is_crypto and 'cfd' in self.contract_type:
                self.close()
                raise ValueError("Cryptocurrencies cannot be traded as cfd.\
                    \nPlease change contract type to classic.")

            self.len_data = len(self.data) - 1
            self.check_dates()
        else:
            self.close()

    def get_default_settings(self):
        return self.get_env_settings(), self.get_network()

    def close(self):
        self.stop = True
        self.event.set()

    def nextDataset(self):
        self.dl.loadFile()
        self.data, self.raw, self._date = self.dl.getData(), self.dl.getRaw(), self.dl.getTime()
        self.len_data = len(self.data) - 1
        self.check_dates()

    def get_env_settings(self):
        self.contract_settings = self.contracts.getSettings()

        c_settings = dict(
            allow_short = self.contract_settings['allow_short'],
            contract_size = self.contract_settings['contract_size'],
            contract_price = self.contract_settings['contract_price'],
            pip_value = self.contract_settings['pip_value'],
            spread = self.contract_settings['spread'],
            contract_type = self.contract_type
        )

        #data_directory = self.dataDirectory,
        meta = dict(
            episodes = self.episode_count,
            targeted_return = self.t_return,
            data_directory = "data/"
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

        reward_settings = dict(
            type = 'pnl',
            no_negative = True,
            period = 0
        )

        states_settings = dict(
            window = 20,
            preprocessing = 'sigmoid'
        )

        env = dict(contract = c_settings,
                   wallet = w_settings,
                   risk_managment = r_settings,
                   base = meta,
                   reward = reward_settings,
                   states = states_settings)

        return env

    def execute(self, action):
        self.current_step['step'] += 1
        self.closed = False
        self.action = action
        if self.step_left == 0:
            self.check_time_before_closing()
        self.step_left -= 1

        self.wallet.pnl['current'] = 0
        if self.current_step['step'] == 0:
            self.contract_settings['contract_price'] = self.contracts.getContractPrice(self.data[self.current_step['step']])
            if self.is_crypto:
                self.contract_settings['contract_size'] = self.wallet.manage_contract_size(self.contract_settings)
        self.price['buy'], self.price['sell'] = self.contracts.calcBidnAsk(self.data[self.current_step['step']])
        self.wallet.manage_exposure(self.contract_settings)        
        self.inventory(self.step_left, action)
        #self.reward(u_pnl=self.wallet.get_current_unrealized_pnl())
        self.wallet.manage_wallet(self.inventory.current_trades, self.price,
                            self.contract_settings)
        
        if len(self.inventory.current_trades) == 0:
            self.pos_delay['current'] += 1
        if self.current_step['step'] > 0:
            self.contract_settings['contract_price'] = self.contracts.getContractPrice(self.data[self.current_step['step']])
            if self.is_crypto:
                self.contract_settings['contract_size'] = self.wallet.manage_contract_size(self.contract_settings)
        '''
        self.train_out.append(act_processing(self.action))
        if self.input_names:
            self.train_in.append([v for k,v in self.state.items()])
        else:
            self.train_in.append(self.state)
        '''
        
        self.wallet.pnl['daily'] += self.wallet.pnl['current']
        self.wallet.pnl['total'] += self.wallet.pnl['current']
        self.def_act()
        self.state = self._state(self.raw)
        self.wallet.daily_process()
        done = True if self.len_data - 1 == self.current_step['step'] else False
           
        if self.wallet.risk_managment['current_max_pos'] < 1:
            done = True
        self.daily_processing(done)
        if done:
            self.episode_process()
        if self.settings['agent']['type'] == 'DEEP':
            self.state = np.array([self.state.ravel()])
        return self.state, done, self.reward.current

    def daily_reset(self):
        self.wallet.daily_reset()
        self.reward.daily_reset()
    
        self.train_in = []
        self.train_out = []

    def reset(self):
        self.tensorOCHL = [[] for _ in range(4)]
        self.step_left = 0
        self.lst_data_full = deque(maxlen=100)
        self.date['day'] = 1
        self.date['month'] = 1
        self.date['year'] = 1
        self.date['total_minutes'] = 1
        self.date['total_day'] = 1
        self.date['total_month'] = 1
        self.date['total_year'] = 1
        self.pos_delay = dict(
            current = 1,
            all = []
        )

        self.start = 0
        self.switch = 0

        self.wallet.reset()
        self.inventory.reset()
        self._state.reset()
        self.current_step['step'] = -1
        self._state(self.raw)
        if self.settings['agent']['type'] == 'DEEP':
            self.state = np.array([self.state.ravel()])
        self.current_step['episode'] += 1
        self.logger._add("Starting episode : " + str(self.current_step['episode']),
                    self._name)
        return self.state
