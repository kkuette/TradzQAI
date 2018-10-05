import pandas as pd
import numpy as np
from tqdm import tqdm
import json
from decimal import *
import time

class Inventory(object):

    def __init__(self):
        self.inventory = []

        self.last_trade = dict(
            open = dict(
                price = 0,
                pos = "",
                fee = 0
            ),
            close = dict(
                price = 0,
                pos = "",
                fee = 0
            ),
            size = 0,
            profit = 0,
            fee = 0
        )

        self.last_closed_order = dict(
            price = 0,
            pos = "",
            fee = 0,
            size = 0
        )

        self.trade_history = []
        self.wallet_len = 0

    def reset(self):
        self.inventory = []

    def get_trade_history(self):
        return self.trade_history

    def get_inventory(self):
        return self.inventory

    def get_last_trade(self):
        return self.last_trade

    def save_last_closing(self, POS):
        '''Save last trade and drop it from inventory'''
        self.last_closed_order['price'] = self.inventory[POS]['Price']
        self.last_closed_order['pos'] = self.inventory[POS]['POS']
        self.last_closed_order['size'] = self.inventory[POS]['Order']
        self.last_closed_order['fee'] = self.inventory[POS]['Fee']
        self.inventory.pop(POS)


    def src_sell(self):
        '''Search for first sell order'''
        for i  in range(self.wallet_len):
            if "SELL" in self.inventory[i]['POS']:
                return (i)
        return (-1)

    def src_buy(self):
        '''Search for first buy order'''
        for i  in range(self.wallet_len):
            if "BUY" in self.inventory[i]['POS']:
                return (i)
        return (-1)

    def add_last_trade(self, env, fee):
        self.last_trade['open']['price'] = self.last_closed_order['price']
        self.last_trade['open']['pos'] = self.last_closed_order['pos']
        self.last_trade['open']['fee'] = self.last_closed_order['fee']
        self.last_trade['fee'] = self.last_trade['open']['fee'] + fee
        if "SELL" in self.last_trade['open']['pos']:
            self.last_trade['close']['price'] = env.price['sell']
            self.last_trade['close']['pos'] = "BUY"
            self.last_trade['profit'] = ((self.last_closed_order['price'] - \
                env.price['sell']) * env.contract_settings['pip_value'] * \
                self.last_closed_order['size'] * env.contract_settings['contract_size'])\
                 + self.last_trade['fee']
            self.last_trade['close']['fee'] = fee
        elif "BUY" in self.last_trade['open']['pos']:
            self.last_trade['close']['price'] = env.price['buy']
            self.last_trade['close']['pos'] = "SELL"
            self.last_trade['profit'] = ((env.price['buy'] - \
                self.last_closed_order['price']) * env.contract_settings['pip_value'] * \
                self.last_closed_order['size'] * env.contract_settings['contract_size']) + \
                self.last_trade['fee']
            self.last_trade['close']['fee'] = fee
        self.last_trade['size'] = self.last_closed_order['size'] * \
            env.contract_settings['contract_size']
        if env.is_crypto:
            env.wallet.manage_trade_total_value(self.last_trade['open']['price'] \
                * env.contract_settings['contract_size'])
            env.wallet.manage_trade_total_value(self.last_trade['close']['price'] \
                * env.contract_settings['contract_size'])
        #tqdm.write(json.dumps(self.last_trade, indent=4))
        #tqdm.write(str(env.wallet.profit['current']))
        #tqdm.write(str(env.reward['current']))
        #tqdm.write(str(env.trade['win'] / (env.trade['win']+env.trade['loss'])))
        #time.sleep(0.2)
        self.trade_history.append(self.last_trade)

    def manage_trade(self, env, profit, fee, idx):
        fee += self.inventory[idx]['Fee']
        env.wallet.profit['current'] = (profit * self.inventory[idx]['Order'] \
            * env.contract_settings['pip_value']) + fee
        if env.wallet.profit['current'] < 0.0:
            env.trade['loss'] += 1
            env.daily_trade['loss'] += 1
            env.reward['current'] = round((profit + fee), 3)
        elif env.wallet.profit['current'] > 0.0 :
            env.trade['win'] += 1
            env.daily_trade['win'] += 1
            env.reward['current'] = round((profit + fee), 3)
        else:
            env.trade['draw'] += 1
            env.daily_trade['draw'] += 1
        env.closed = True

    def trade_closing(self, env):
        if self.wallet_len > 0 and env.step_left == self.wallet_len:
            current = self.inventory[0]['Price']
            if "SELL" in self.inventory[0]['POS']:
                ret = env.price['buy'] - current
                fee = env.wallet.calc_fees(env.price['sell'] * \
                    self.inventory[0]['Order'] * \
                    env.contract_settings['contract_size'])
            elif "BUY" in self.inventory[0]['POS']:
                ret = current - env.price['sell']
                fee = env.wallet.calc_fees(env.price['buy'] * \
                    self.inventory[0]['Order'] * \
                    env.contract_settings['contract_size'])
            ret *= env.contract_settings['contract_size']
            self.manage_trade(env, ret, fee, 0)
            self.save_last_closing(0)
            self.add_last_trade(env, fee)
            return True
        return False

    def stop_loss(self, env):
        '''Stop loss'''
        self.wallet_len = len(self.inventory)
        current = 0
        for i in range(self.wallet_len):
            current = self.inventory[i]['Price']
            if "SELL" in self.inventory[i]['POS']:
                ret = env.price['buy'] - current
                fee = env.wallet.calc_fees(env.price['buy'] *\
                    self.inventory[i]['Order'] * \
                    env.contract_settings['contract_size'])
            elif "BUY" in self.inventory[i]['POS']:
                ret = current - env.price['sell']
                fee = env.wallet.calc_fees(env.price['sell'] * \
                    self.inventory[i]['Order'] * \
                    env.contract_settings['contract_size'])
            if abs(ret) >= env.wallet.risk_managment['stop_loss'] and ret < 0:
                ret *= env.contract_settings['contract_size']
                self.manage_trade(env, ret, fee, i)
                self.save_last_closing(i)
                self.add_last_trade(env, fee)
                return True
        return False

    def inventory_managment(self, env):
        POS =  self.wallet_len # Number of contract in inventory
        if 1 == env.action: # Buy
            POS_SELL = self.src_sell() # Check if SELL order in inventory
            if POS_SELL == -1 and POS < env.wallet.risk_managment['current_max_pos']\
                and env.step_left > env.wallet.risk_managment['current_max_pos']: # Open order
                buy = dict(
                    Price = env.price['buy'],
                    POS = "BUY",
                    Order = env.wallet.risk_managment['max_order_size'],
                    Fee = env.wallet.calc_fees(env.wallet.risk_managment['max_order_size']\
                        * env.price['buy'] * env.contract_settings['contract_size'])
                )
                self.inventory.append(env.price['buy'], env.contract_settings['contract_size'])
                if env.api:
                    env.api.buy(env.contract_settings['contract_size'])
            elif POS_SELL != -1:# Close order in inventory
                '''Selling order from inventory list
                Calc profit and total profit
                Add last Sell order to env'''
                profit = (self.inventory[POS_SELL]['Price'] - env.price['sell'])\
                    * env.contract_settings['contract_size']
                fee = env.wallet.calc_fees(env.price['sell'] * \
                    self.inventory[POS_SELL]['Order'] * \
                    env.contract_settings['contract_size'])
                self.manage_trade(env, profit, fee, POS_SELL)
                self.save_last_closing(POS_SELL)
                self.add_last_trade(env, fee)
                if env.api:
                    env.api.buy(env.contract_settings['contract_size'])
            else:
                env.reward['current'] = 0

        elif 2 == env.action: # Sell
            POS_BUY = self.src_buy() # Check if BUY order in inventory
            if POS_BUY == -1 and POS < env.wallet.risk_managment['current_max_pos']\
                and env.contract_settings['allow_short'] is True and \
                env.wallet.risk_managment['current_max_pos'] and env.step_left >\
                env.wallet.risk_managment['current_max_pos']: #Open order
                sell = dict(
                    Price = env.price['sell'],
                    POS = "SELL",
                    Order = env.wallet.risk_managment['max_order_size'],
                    Fee = env.wallet.calc_fees(env.wallet.risk_managment['max_order_size']\
                        * env.price['sell'] * env.contract_settings['contract_size'])
                )
                self.inventory.append(sell)
                if env.api:
                    env.api.sell(env.contract_settings['contract_size'])
            elif POS_BUY != -1:# Close order in inventory
                '''Selling order from inventory list
                Calc profit and total profit
                Add last Sell order to env'''
                profit = (env.price['buy'] - self.inventory[POS_BUY]['Price'])\
                 * env.contract_settings['contract_size']
                fee = env.wallet.calc_fees(env.price['buy'] * \
                    self.inventory[POS_BUY]['Order'] * \
                    env.contract_settings['contract_size'])
                self.manage_trade(env, profit, fee, POS_BUY)
                self.save_last_closing(POS_BUY)
                self.add_last_trade(env, fee)
                if env.api:
                    env.api.sell(env.contract_settings['contract_size'])
            else:
                env.reward['current'] = 0
        else: # Hold
            env.reward['current'] = 0
