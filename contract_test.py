'''
from tools import *
import matplotlib.pyplot as plt
import numpy as np

dl = dataLoader(directory="data/train/")

for file in dl.files:
    dl.loadFile()
    plt.figure(num=file.replace("coinbaseEUR_data_daily_i/BTC_EUR_2018_08/", ""))
    plt.subplot(411)
    plt.plot(np.array(dl.getRaw()['Price']), color='blue')
    plt.plot(np.array(dl.getRaw()['EMA20']), color='red')
    plt.plot(np.array(dl.getRaw()['EMA50']), color='green')
    plt.plot(np.array(dl.getRaw()['EMA100']), color='black')
    plt.title("Price, EMA20, 50, 100")
    plt.subplot(412)
    plt.plot(np.array(dl.getRaw()['Volume']), color='black')
    plt.title("Volume")
    plt.subplot(413)
    plt.plot(np.array(dl.getRaw()['RSI']), color='blue')
    plt.title("RSI")
    plt.subplot(414)
    plt.plot(np.array(dl.getRaw()['MACD']), color='blue')
    plt.title("MACD")
    plt.show()
    '''
from API import Api
import time
import sys

a = Api("cbpro", passphrase=passphrase, b64=b64,
    key=key, url='https://api-public.sandbox.pro.coinbase.com')
a.start()
try:
    while True:
        time.sleep(0.2)
        o = input("buy or sell ? ")
        if "buy" in o:
            a.buy(float(input("Which size would you buy ? ")))
        elif "sell" in o:
            a.sell(float(input("Which size would you buy ? ")))
        else:
            print ("I don't understand, please retry\n")
        time.sleep(1)
except KeyboardInterrupt:
    a.stop()
    sys.exit(0)
