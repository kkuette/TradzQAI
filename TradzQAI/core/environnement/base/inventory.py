from .trades import trades
from .orders import orders

from tqdm import tqdm

class Inventory:

    def __init__(self, wallet=None, price=None, reward=None, 
        contract_settings=None, api=None):
        '''
        Inventory class for trade management

            args:
                wallet: (class) all wallet settings
                price: (dict) buy and sell price
                reward: (class)
                api: (class)
        '''
        self.api = api
        self.wallet = wallet
        self.price = price
        self.reward = reward
        self.contract_settings = contract_settings
        self.reset()

    def reset(self):
        self.trades = trades()
        self.orders = orders()
        self.current_trades = []
        self.number_order = 0
        self.current_strat = 'hold'

    def _open(self, price, side, size, fee):
        ''' open trade '''
        # create a new trade and create an open order
        if self.api:
            print ("Open %s %s @ %s" % (self.current_strat,
                self.price[self.current_strat], 
                self.contract_settings['contract_size']))
            self.trades()(getattr(self.api, side)(size, 
                allocated_funds=price * size))
        else:
            self.trades()(self.orders(price, side, size, fee))
        # add opened trade to trade list
        self.current_trades.append(self.trades.current)

    def _close(self, price, side, size, fee, _id=0):
        ''' close trade '''
        if self.api:
            # Check if order is valid
            if self.current_trades[_id].open.price != 0:
                print ("Close %s %s @ %s" % (self.invert_side(),
                    self.price[self.invert_side()], 
                    self.contract_settings['contract_size']))
                # close a trade and create a close order from api
                self.trades()(getattr(self.api, side)(size))
        else:
            # close a trade and create a close order
            self.current_trades[_id](self.orders(price, 
                side, size, fee))
            # add reward
            if self.current_trades[_id].pnl > 0:
                self.trades.win += 1
            elif self.current_trades[_id].pnl < 0:
                self.trades.loose += 1
            else:
                self.trades.draw += 1
            self.wallet.pnl['current'] = self.current_trades[_id].pnl
            self.reward(pnl=round(self.current_trades[_id].pnl, 3))
            # delete closed trade from trades list
            self.current_trades.pop(_id)
            # reset strat
            if len(self.current_trades) == 0:
                self.current_strat = 'hold'
        

    def invert_side(self):
        if self.current_strat == 'buy':
            return 'sell'
        elif self.current_strat == 'sell':
            return 'buy'

    def stop_loss(self):
        ''' 
        stop loss
            check if u_pnl is greater than stop loss from risk managment,
            force close if it's greater
        '''
        for i in range(len(self.current_trades)):
            u_pnl = self.current_trades[i].open.price - self.price[self.invert_side()]
            if u_pnl <= -self.wallet.risk_managment['stop_loss']:
                self._close(self.price[self.invert_side()], self.invert_side(),
                    self.current_trades[i].open.size,
                    self.wallet.calc_fees(self.price[self.invert_side()] * \
                        self.current_trades[i].open.size), _id=i)
                return True
        return False

    def force_close(self, step_left):
        '''
        force close
            check time left before market close or day change and close
            if is time before closing is equal to trade number in inventory
        '''
        if self.number_order > 0 and step_left == self.number_order:
            self._close(self.price[self.invert_side()], self.invert_side(),
                self.current_trades[0].open.size,
                self.wallet.calc_fees(self.price[self.invert_side()] * \
                        self.wallet.risk_managment['max_order_size'] * \
                        self.contract_settings['contract_size'])
                )
            return True
        return False

    def manage(self, step_left, action):
        if action == 1: # buy
            # Check if it can open a new opsition
            if not self.current_strat == 'sell' and \
                self.number_order < self.wallet.risk_managment['current_max_pos'] and \
                step_left > self.wallet.risk_managment['current_max_pos']:
                # set current side to new current side and open order
                self.current_strat = 'buy'
                self._open(self.price[self.current_strat], self.current_strat, 
                    self.wallet.risk_managment['max_order_size'] * \
                    self.contract_settings['contract_size'], 
                    self.wallet.calc_fees(self.price[self.current_strat] * \
                        self.wallet.risk_managment['max_order_size'] * \
                        self.contract_settings['contract_size'])
                )
            elif self.current_strat == 'sell':
                self._close(self.price[self.invert_side()], self.invert_side(),
                    self.wallet.risk_managment['max_order_size'] * \
                    self.contract_settings['contract_size'], 
                    self.wallet.calc_fees(self.price[self.invert_side()] * \
                        self.wallet.risk_managment['max_order_size'] * \
                        self.contract_settings['contract_size'])
                )
            else:
                self.reward(pnl=0)
        elif action == 2: # sell
            # Check if it can open a new opsition
            if not self.current_strat == 'buy' and \
                self.number_order < self.wallet.risk_managment['current_max_pos'] and \
                step_left > self.wallet.risk_managment['current_max_pos']and \
                self.contract_settings['allow_short']:
                # set current side to new current side and open order
                self.current_strat = 'sell'
                self._open(self.price[self.current_strat], self.current_strat, 
                    self.wallet.risk_managment['max_order_size'] * \
                    self.contract_settings['contract_size'], 
                    self.wallet.calc_fees(self.price[self.current_strat] * \
                        self.wallet.risk_managment['max_order_size'] * \
                        self.contract_settings['contract_size'])
                )
            elif self.current_strat == 'buy':
                self._close(self.price[self.invert_side()], self.invert_side(),
                    self.wallet.risk_managment['max_order_size'] * \
                    self.contract_settings['contract_size'], 
                    self.wallet.calc_fees(self.price[self.invert_side()] * \
                        self.wallet.risk_managment['max_order_size'] * \
                        self.contract_settings['contract_size'])
                )
            else:
                self.reward(pnl=0)
        else: # hold
            self.reward(pnl=0)
    
    def __call__(self, step_left, action):
        self.number_order = len(self.current_trades)
        if not self.stop_loss():
            if not self.force_close(step_left):
                self.manage(step_left, action)

    