import numpy as np
import pandas as pd

import time
import os
import math
from threading import Thread
from collections import deque
from tqdm import tqdm
import subprocess

from .indicators import Indicators

class dataLoader(Thread):

    def __init__(self, directory="data/", mode=None):
        self.data = deque(maxlen=1)
        self.mode = mode
        self.raw = deque(maxlen=1)
        self.time = deque(maxlen=1)
        self.files_index = 0
        self.setDirectory(directory)
        self.dat = None
        self.logger = None


        Thread.__init__(self)

    def setDirectory(self, directory):
        self.files = []
        self.files_count = 0
        self.directory = directory
        if not self.directory:
            raise ValueError("There is no directory")
        if not os.path.exists(self.directory):
            raise ValueError("%s does not exist" % directory)
        self.checkDirectory(self.directory)

    def setLogger(self, logger):
        self.logger = logger
        self.logger.new_logs(self.mode+"_data")

    def getData(self):
        return self.data[0]

    def getRaw(self):
        return self.raw[0]

    def getTime(self):
        return self.time[0]

    def checkDirectory(self, directory):
        files = os.listdir(directory)
        for file in files:
            f = directory + file
            if os.path.isdir(f):
                self.checkDirectory(f+"/")
            elif os.path.isfile(f):
                self.files.append(f)
                self.files_count += 1

    def getStockDataVec(self, key):
            path = key#"data/" + key + ".csv"
            if not os.path.exists(path):
                raise ValueError("Your stock {} is not in data/ directory.".format(key))
            vec = None
            row = None
            chunksize = 10000
            nlines = subprocess.check_output('wc -l %s' % path, shell=True)
            nlines = int(nlines.split()[0])
            chunksize = nlines // 10
            lines = subprocess.check_output('head %s' % path, shell=True).decode()
            lines = lines.split('\n')[0]

            if ',' in lines:
                sep = ','
                len_row = len(lines.split(sep))
                if len_row == 4:
                    #types = dict(BID='np.float64', ASK='np.float64', Volume='np.float64')
                    #names = ['ID', 'Time', 'Price', 'Volume']
                    names = ['Time', 'BID', 'ASK', 'Volume']
                elif len_row == 3:
                    #types = dict(Price='np.float64', Volume='np.float64')
                    names = ['Time', 'Price', 'Volume']
                elif len_row == 9:
                    names = ['Time', 'Price', 'Volume', 'RSI', 'MACD', 'Volatility', 'EMA20', 'EMA50', 'EMA100']
            elif ';' in lines:
                sep = ';'
                len_row = len(lines.split(sep))
                if len_row == 6:
                    #types = dict(Open=np.float64, High=np.float64, Low=np.float64, Close=np.float64)
                    names = ['Time', 'Open', 'High', 'Low', 'Close', '']

            for i in range(0, nlines, chunksize):
                df = pd.read_csv(path, header=None, sep=sep, nrows=chunksize,
                    skiprows=i, low_memory=False)
                df.columns = names
                if row is not None:
                    row = row.append(df, ignore_index=True)
                else:
                    row = df.copy(deep=True)

            time = row['Time'].copy(deep=True)

            if len_row == 4 and ',' in sep:
                vec = row['ASK'].copy(deep=True)
                row.drop(row.columns[[0]], axis=1, inplace=True)

            elif len_row == 3 and ',' in sep:
                vec = row['Price'].copy(deep=True)
                row.drop(row.columns[[0]], axis=1, inplace=True)

            elif len_row == 9 and ',' in sep:
                vec = row['Price'].copy(deep=True)
                row.drop(row.columns[[0,5,6,7,8]], axis=1, inplace=True)

            elif len_row == 6 and ';' in sep:
                vec = row['Close'].copy(deep=True)
                row.drop(row.columns[[0,1,2,5]], axis=1, inplace=True)

            return vec, row, time

    def loadFile(self):
        if self.files_index == self.files_count:
            self.data.append(None)
            self.raw.append(None)
            self.time.append(None)
            return
        tmp_data, tmp_raw, tmp_time = self.getStockDataVec(self.files[self.files_index])
        if self.logger:
            self.logger._add(self.files[self.files_index], self.mode+"_data")

        self.files_index += 1
        self.data.append(tmp_data)
        self.raw.append(tmp_raw)
        self.time.append(tmp_time)

    def run(self):
        self.loadFile()


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def str2bool(value):
    if str(value).lower() in ("yes", "y", "true",  "t", "1", "1.0"): return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0"): return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))

############################

# prints formatted price
def formatPrice(n):
        return "{0:.2f}".format(n) + " €"

# returns the sigmoid
def sigmoid(x):
    try:
        exp = math.exp(-x)
    except:
        exp = float('Inf')
    return 1 / (1 + exp)

# returns an an n-day state representation ending at time t
def getState(data, t, n, fn_process=sigmoid):
        d = t - n + 1
        temp = []
        for col in data.columns:
            tmp = np.asarray(data[col])
            block = tmp[d:t + 1] if d >= 0 else np.concatenate([-d * [tmp[0]]] + [tmp[0:t + 1]])
            res = []
            for i in range(n - 1):
                if ("Price" or "EMA") in col:
                    res.append(fn_process(block[i + 1] - block[i]))
                else:
                    res.append(block[i])
            temp.append(res)
        datas = []
        for idx in range(len(temp[0])):
            datas.append([temp[i][idx] for i in range(len(data.columns))])
        return np.array(datas)

def act_processing(act):
    if act == 1:
        return ([1, 0, 0])
    elif act == 2:
        return ([0, 1, 0])
    else:
        return ([0, 0, 1])

def style(s, style):
    return style + s + '\033[0m'


def green(s):
    return style(s, '\033[92m')


def blue(s):
    return style(s, '\033[94m')


def yellow(s):
    return style(s, '\033[93m')


def red(s):
    return style(s, '\033[91m')


def pink(s):
    return style(s, '\033[95m')


def bold(s):
    return style(s, '\033[1m')


def underline(s):
    return style(s, '\033[4m')
