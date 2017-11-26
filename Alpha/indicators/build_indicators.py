import pandas as pd

from indicators.exponential_moving_average import exponential_moving_average as ema
from indicators.volatility import volatility as vol
from indicators.stochastic import percent_k as K
from indicators.stochastic import percent_d as D
from indicators.relative_strength_index import relative_strength_index as RSI

class indicators():

    def __init__(self):

        self.bb_period = 20
        self.rsi_period = 14
        self.sd_period = 0
        self.sv_period = 0
        self.stoch_period = 14
        self.volatility_period = 20

    def build_indicators(self, data):
        names = ['RSI', 'Volatility']#, 'Stoch_D', 'Stock_K', 'EMA20', 'EMA50','EMA100']
        indicators = pd.DataFrame(columns = names)
        print ("Building RSI")
        indicators['RSI'] = RSI(data, self.rsi_period)
        print ("Building Volatility")
        indicators['Volatility'] = vol(data, self.volatility_period)
        '''
        print ("Building Stoch_D")
        indicators['Stoch_D'] = D(data, self.stoch_period)
        print ("Building Stoch_K")
        indicators['Stock_K'] = K(data, self.stoch_period)
        print ("Building EMA20")
        indicators['EMA20'] = ema(data, 20)
        print ("Building EMA50")
        indicators['EMA50'] = ema(data, 50)
        print ("Building EMA100")
        indicators['EMA100'] = ema(data, 100)
        '''
        return indicators
