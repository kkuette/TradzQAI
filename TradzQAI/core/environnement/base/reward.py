import numpy as np

class Reward:

    def __init__(self, type='pnl', no_neg=True, period=0):
        ''' Reward class
        args:
            type: (str) reward calculation function
            no_neg: (bool) if true it get only positive reward
            period: (int) period for sma
        '''
        self.no_neg = no_neg
        if type == 'pnl':
            self.func = self.pnl
        elif type == 'unrealized_pnl':
            self.func = self.unrealized_pnl
        elif type == 'unrealized_pnl_sma':
            self.func = self.unrealized_pnl_sma
        else:
            raise ValueError('Reward have no function called %s' % type)

        self.call_id = -1
        self.period = period

        self.current = 0
        self.daily = []
        self.episode = []
        self.total = []

    def add_reward(self, reward):
        self.current = reward
        self.daily.append(reward)

    def get_daily_reward(self):
        return np.sum(self.daily)

    def get_episode_reward(self):
        return np.sum(self.episode)

    def get_total_reward(self):
        return np.sum(self.total)

    def daily_reset(self):
        self.current = 0
        self.episode.append(np.sum(self.daily))
        self.daily = []
        
    def episode_reset(self):
        self.total.append(np.sum(self.episode))
        self.episode = []

    def reset(self):
        self.call_id = -1
        self.total = []

    def pnl(self):
        return self.current

    def unrealized_pnl(self):
        return self.current

    def unrealized_pnl_sma(self):
        if self.call_id > 0:
            if self.call_id > self.period:
                return np.average(self.daily[self.call_id-self.period:])
            else:
                return np.average(self.daily)
        else:
            return self.current

    def no_negative(self, reward):
        return max(0, reward)

    def __call__(self, u_pnl=None, pnl=None):
        if 'pnl' == self.func.__name__ and pnl:
            if self.no_neg:
                self.add_reward(self.no_negative(pnl))
            else:
                self.add_reward(pnl)
        elif 'pnl' != self.func.__name__ and u_pnl:
            if self.no_neg:
                self.add_reward(self.no_negative(u_pnl))
            else:
                self.add_reward(u_pnl)
        self.call_id += 1
        return self.func()