import pandas as pd

from tools.indicators.exponential_moving_average import exponential_moving_average as ema
from tools.indicators.volatility import volatility as vol
from tools.indicators.stochastic import percent_k as K
from tools.indicators.stochastic import percent_d as D
from tools.indicators.relative_strength_index import relative_strength_index as RSI
from tools.indicators.moving_average_convergence_divergence import moving_average_convergence_divergence as macd
from tools.indicators.bollinger_bands import bandwidth as bb

class Indicators():

    def __init__(self, settings=None):

        self.bb_period = 20
        self.rsi_period = 14
        self.sd_period = 0
        self.sv_period = 0
        self.stoch_period = 14
        self.volatility_period = 20
        self.macd_long = 24
        self.macd_short = 12
        self.ema_periods = [20, 50, 100]
        self.settings = settings
        self.build_func = None
        self.names = []

    def add_building(self, settings=None):
        if settings:
            self.settings = settings
        if self.settings:
            self.build_func = []
            for key, value in self.settings.items():
                if not value:
                    continue
                elif "RSI" == key and value:
                    self.names.append('RSI')
                    if 'default' != value:
                        self.rsi_period = value
                    self.build_func.append([RSI, 'RSI', self.rsi_period])
                elif "MACD" == key and value:
                    self.names.append('MACD')
                    if 'default' != value:
                        self.macd_long = value[1],
                        self.macd_short = value[0]
                    self.build_func.append([macd, 'MACD', [self.macd_short, self.macd_long]])
                elif "Volatility" == key and value:
                    self.names.append('Volatility')
                    if 'default' != value:
                        self.volatility_period = value
                    self.build_func.append([vol, 'Volatility', self.volatility_period])
                elif "EMA" == key and value:
                    if 'default' != value:
                        for values in value:
                            self.names.append('EMA'+str(values))
                            self.build_func.append([ema, 'EMA'+str(values), values])
                elif "Bollinger_bands" == key and value:
                    self.names.append('Bollinger_bands')
                    if 'default' != value:
                        self.bb_period = value
                    self.build_func.append([bb, 'Bollinger_bands', self.bb_period])
                elif "Stochastic" == key and value:
                    self.names.append('Stochastic_D')
                    self.names.append('Stochastic_K')
                    if 'default' != value:
                        self.stoch_period = value
                    self.build_func.append([D, 'Stochastic_D', self.stoch_period])
                    self.build_func.append([K, 'Stochastic_K', self.stoch_period])

    def build_indicators(self, data):
        if not self.build_func:
            raise ValueError("No indicators to build.")
        indicators = pd.DataFrame(columns=self.names)
        for idx in self.build_func:
            print (idx[1])
            if "MACD" in idx[1]:
                indicators[idx[1]] = idx[0](data, idx[2][0], idx[2][1])
            else:
                indicators[idx[1]] = idx[0](data, idx[2])
        return indicators
