from tools import Indicators, getStockDataVec

import pandas as pd


if __name__ == '__main__':
    indicators = dict(
        RSI = 'default',
        MACD = 'default',
        Volatility = 'default',
        EMA = [20, 50, 100],
        Bollinger_bands = None,
        Stochastic = None
    )

    file = "coinbaseEUR"
    path = "data/" + file + "_i" + ".csv"
    raw_name = 'Price'

    _, raw, _ = getStockDataVec(file)
    indics = Indicators()
    indics.add_building(settings=indicators)
    raw = raw.join(indics.build_indicators(raw[raw_name]))
    raw.to_csv(path, sep=',')
