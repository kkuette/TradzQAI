from collections import deque
from decimal import *
import numpy as np
from tqdm import tqdm

class Wallet(object):

    def __init__(self):

        self.pnl = dict(
            current = 0,
            daily = 0,
            total = 0,
            percent = 0
        )

        self.unrealized_pnl = []

        self.risk_managment = dict(
            max_pos = 10,
            max_order_size = 1,
            current_max_pos = 0,
            exposure = 10,
            stop_loss = 20,
            capital_exposure = 0
        )

        self.settings = dict(
            capital = 200,
            fee = 0.3,
            used_margin = 0,
            GL_pip = 0,
            GL_pnl = 0
        )

        self.product_wallet = 0

        self.historic = dict(
            mean_return = [],
            sharp_ratio = [],
            max_return = [],
            max_drawdown = [],
            capital = []
        )

        self.episode = dict(
            mean_return = [],
            sharp_ratio = [],
            max_drawdown = [],
            max_return = [],
            _return = [],
            capital = []
        )

        self.daily = dict(
            mean_return = [],
            sharp_ratio = [],
            max_drawdown = [],
            max_return = [],
            _return = [],
            capital = []
        )

        self.firstCheck = True
        self.min_size = 0.001

    def init_default(self):
        self.settings['saved_capital'] = self.settings['capital']
        self.settings['usable_margin'] = self.settings['capital']

    def get_current_unrealized_pnl(self):
        return self.unrealized_pnl[-1:]

    def daily_reset(self):
        self.unrealized_pnl = []
        self.pnl['daily'] = 0
        self.daily['mean_return'] = []
        self.daily['sharp_ratio'] = []
        self.daily['max_drawdown'] = []
        self.daily['max_return'] = []
        self.daily['capital'] = []
        self.daily['_return'] = []

    def reset(self):
        self.settings['capital'] = self.settings['saved_capital']
        self.settings['usable_margin'] = self.settings['saved_capital']
        self.settings['used_margin'] = 0
        self.settings['GL_pip'] = 0
        self.settings['GL_pnl'] = 0
        self.risk_managment['max_order_size'] = 1
        self.risk_managment['current_max_pos'] = 0
        self.pnl['total'] = 0
        self.pnl['percent'] = 0
        self.unrealized_pnl = []
        self.episode['mean_return'] = []
        self.episode['sharp_ratio'] = []
        self.episode['max_drawdown'] = []
        self.episode['max_return'] = []
        self.episode['capital'] = []
        self.episode['_return'] = []
        self.total_trade_value = 0

    def historic_process(self):
        self.historic['mean_return'].append(self.episode['mean_return'][len(self.episode['mean_return']) - 1])
        self.historic['sharp_ratio'].append(self.episode['sharp_ratio'][len(self.episode['sharp_ratio']) - 1])
        self.historic['max_drawdown'].append(self.episode['max_drawdown'][len(self.episode['max_drawdown']) - 1])
        self.historic['max_return'].append(self.episode['max_return'][len(self.episode['max_return']) - 1])
        self.historic['capital'].append(self.episode['capital'][len(self.episode['capital']) - 1])

    def episode_process(self):
        self.episode['mean_return'].append(np.mean(self.episode['_return']))
        self.episode['sharp_ratio'].append(self.calc_sharp_ratio(self.episode['_return'], (len(self.episode['_return']) - 1)))
        self.episode['max_drawdown'].append(self.calc_max_drawdown(np.array(self.episode['capital'])))
        self.episode['max_return'].append(self.calc_max_return(np.array(self.episode['capital'])))
        self.pnl['percent'] = self.pnl['total'] / self.settings['saved_capital'] * 100

    def daily_process(self):
        self.episode['capital'].append(self.settings['capital'])
        self.episode['_return'].append(self.pnl['current'])

    def calc_fees(self, price):
        return price - ((1 + (self.settings['fee'] / 100)) * price)

    def calc_sharp_ratio(self, _return, period):
        if np.sum(_return[len(_return) - 1 - period:]) == 0:
            return 0
        std = np.std(_return[len(_return) - 1 - period:], ddof=1)
        mean = np.mean(_return[len(_return) - 1 - period:])
        sqrt = np.sqrt(period)
        return sqrt * mean / std

    def calc_max_return(self, capital):
        if len(capital) < 2:
            return 0
        max = np.argmax(np.maximum.accumulate(capital) + capital)
        if max == 0:
            return 0
        min_before_max = np.argmin(capital[:max])
        _return = 100 * (capital[max] - capital[min_before_max]) / capital[min_before_max]
        return _return

    def calc_max_drawdown(self, capital):
        if len(capital) < 2:
            return 0
        min = np.argmax(np.maximum.accumulate(capital) - capital)
        if min == 0:
            return 0
        max_before_min = np.argmax(capital[:min])
        drawdown = 100 * (capital[min] - capital[max_before_min]) / capital[max_before_min]
        return drawdown

    def manage_trade_total_value(self, value):
        self.total_trade_value += value
        if self.settings['fee'] != 0:
            if self.total_trade_value >= 10000000 and self.total_trade_value <= 100000000:
                self.settings['fee'] = 0.2
            elif self.total_trade_value > 100000000:
                self.settings['fee'] = 0.1

    def manage_wallet(self, inventory, price, contract_settings, api=False):
        avg = 0
        i = 0
        while i < len(inventory):
            avg += inventory[i].open.price
            i += 1
        if i > 0:
            avg /= i
            if "sell" in inventory[0].open.side:
                self.settings['GL_pnl'] = (avg - price['buy']) * i * contract_settings['pip_value'] * contract_settings['contract_size'] + \
                    (self.calc_fees(avg * contract_settings['contract_size']) * i)
            elif "buy" in inventory[0].open.side:
                self.settings['GL_pnl'] = (price['sell'] - avg) * i * contract_settings['pip_value'] * contract_settings['contract_size'] + \
                    (self.calc_fees(avg * contract_settings['contract_size']) * i)
        else:
            self.settings['GL_pnl'] = 0

        self.settings['capital'] += self.pnl['current']
        self.settings['used_margin'] = self.settings['GL_pnl']
        self.settings['usable_margin'] = self.risk_managment['capital_exposure'] - self.settings['used_margin']
        if self.settings['used_margin'] < 0:
            self.settings['used_margin'] = 0
        self.unrealized_pnl.append(self.settings['GL_pnl'])

    def manage_exposure(self, contract_settings, api=False):
        self.risk_managment['capital_exposure'] = self.settings['capital'] - (self.settings['capital'] * (1 - (self.risk_managment['exposure'] / 100)))
        try:
            max_order_valid = self.risk_managment['capital_exposure'] // (contract_settings['contract_size'] * (contract_settings['contract_price'] * contract_settings['pip_value']))
        except:
            max_order_valid = 0
        if max_order_valid <= self.risk_managment['max_pos']:
            self.risk_managment['current_max_pos'] = max_order_valid
            self.risk_managment['max_order_size'] = 1
        else:
            self.risk_managment['current_max_pos'] = self.risk_managment['max_pos']
            extra_order = max_order_valid - self.risk_managment['max_pos']
            if extra_order >= self.risk_managment['max_pos']:
                self.risk_managment['max_order_size'] = int(max_order_valid // self.risk_managment['max_pos'])
            else:
                self.risk_managment['max_order_size'] = 1
        if self.risk_managment['current_max_pos'] < 1 and self.firstCheck and not api:
            raise ValueError('current_max_pos : {:.3f} We cant afford any contract. Please check wallet settings.'.format(self.risk_managment['current_max_pos']))
        else:
            self.firstCheck = False

    def manage_contract_size(self, contract_settings, api=False):
        self.risk_managment['capital_exposure'] = self.settings['capital'] - (self.settings['capital'] * (1 - (self.risk_managment['exposure'] / 100)))
        size = self.risk_managment['capital_exposure'] / (contract_settings['contract_price'] * contract_settings['pip_value'])
        idx = self.risk_managment['max_pos']
        self.min_size = 0.001
        tmp_size = size / idx
        while idx > 1 and tmp_size <= self.min_size:
            idx = int(idx * (1-size))
            tmp_size = size / idx
        size = float(Decimal(str(tmp_size)).quantize(Decimal('.0000001'), rounding=ROUND_DOWN))
        if (size < self.min_size or idx < 1) and self.firstCheck and not api:
            raise ValueError("Your contract size {:.4f} is too small, or you cannot afford any contract max pos : {}. Please check your settings".format(size, idx))
        #elif size < 1.0:
            #return size
        elif size < self.min_size:
            return 0
        else:
            return size
