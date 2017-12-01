import numpy as np
import pandas as pd
import math

import matplotlib.pyplot as plt

# prints formatted price
def formatPrice(n):
        return ("-$" if n < 0 else "$") + "{0:.2f}".format(abs(n))

# returns the vector containing stock data from a fixed file
def getStockDataVec(key):
        vec = []
        rsi = []
        path = "data/" + key + ".csv"
        lines = open(path, "r").read().splitlines()
        #names = ['ID', 'Time', 'Open', 'High', 'Low', 'Close', 'RSI', 'Volatility']
        #names = ['Time', 'Open', 'High', 'Low', 'Close', '']
        names = ['ID', 'Time', 'BID', 'ASK', 'RSI']
        row = pd.read_csv(path, sep=';', header=0, names=names)#, names = names)
        '''
        for line in lines[1:]:
            vec.append(float(line.split(";")[4]))
        '''
        for l in range(len(row['BID'])):
            vec.append(row['BID'].iloc[l])
            rsi.append(row['Time'].iloc[l])

        return vec, rsi

# returns the sigmoid
def sigmoid(x):
        return 1 / (1 + math.exp(-x))

# returns an an n-day state representation ending at time t
def getState(data, t, n, rsi):
        d = t - n + 1
        block = data[d:t + 1] if d >= 0 else -d * [data[0]] + data[0:t + 1] # pad with t0
        block_r = rsi[d:t + 1] if d >= 0 else -d * [rsi[0]] + rsi[0:t + 1] # pad with t0
        res = []
        for i in range(n - 1):
            #res.append(sigmoid(block_r[i + 1] - block_r[i]))

            res.append(sigmoid(block[i + 1] - block[i]))


        '''
        plt.plot(res, color='green', label='sig(data)')
        plt.plot(res2, color='red', label='sig(data)*volatility')
        plt.show()
        '''

        return np.array([res])
