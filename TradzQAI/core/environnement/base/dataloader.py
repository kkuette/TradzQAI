import pandas as pd
import os
from collections import deque
import subprocess
from datetime import datetime

from TradzQAI.tools import Indicators

# Indicators dict should be added in environnement configuration 
indicators = dict(
        RSI = 'default',
        MACD = 'default',
        Volatility = None,
        EMA = None,
        Bollinger_bands = None,
        Stochastic = None
    )

class dataLoader:

    def __init__(self, directory="data/", mode=None,
            time_mode='daily', api=None, trading_frequency='1M'):
        ''' 
        data loading class

            args:
                directory: (str) Data location path
                mode: (str) eval or train from env
                time_mode: (str) used only for concatenation of some datasets
                api: (api class) get data from api
        '''
        self.data = deque(maxlen=1)
        self.mode = mode
        self.raw = deque(maxlen=1)
        self.time = deque(maxlen=1)
        self.api = api
        self.ticks = []
        self.raw_ticks = []
        self.columns = ['Time', 'Price', 'Volume']
        self.dat = None
        self.logger = None
        self.data_max_len = 100
        self.files_index = 0
        self.file_month_index = 0
        self.files_month = []
        self.cmonth = []
        self.time_mode = time_mode
        if not self.api:
            self.setDirectory(directory)
            if self.time_mode == 'month':
                self.concatPerMonth()
        else:
            self.indics = Indicators()
            self.indics.add_building(settings=indicators)

    def reset(self):
        self.files_index = 0
        self.raw = deque(maxlen=1)
        self.time = deque(maxlen=1)
        self.data = deque(maxlen=1)

    def setDirectory(self, directory):
        ''' 
        set directory for data loading
            args:
                directory: (str) Data location path
        '''
        self.files = []
        self.files_count = -1
        self.directory = directory
        if not os.path.exists(self.directory):
            raise ValueError("%s does not exist" % directory)
        self.checkDirectory(self.directory)

    def setLogger(self, logger):
        ''' logger for data path saving '''
        self.logger = logger
        self.logger.new_logs("data_"+self.mode)

    def getData(self):
        return self.data[0]

    def getRaw(self):
        return self.raw[0]

    def getTime(self):
        return self.time[0]

    def checkDirectory(self, directory):
        ''' go through directories and check for files '''
        files = os.listdir(directory)
        idx = 0
        for file in files:
            f = directory + file
            if os.path.isdir(f):
                self.checkDirectory(f+"/")
            elif os.path.isfile(f):
                self.files.append(f)
                self.files_count += 1
                idx += 1
        if idx > 0:
            self.files_month.append(idx)

    def getStockDataVec(self, key):
        ''' 
        Open path and get data
            args:
                key: (str) data path
            return:
                vec: (pandas dataframe) price array
                row: (pandas dataframe) all array except time
                time: (pandas dataframe) time array
        '''
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
            elif len_row == 6:
                names = ['Time', 'Price', 'Volume', 'RSI', 'MACD', 'Volatility']#, 'EMA20', 'EMA50', 'EMA100']
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
        elif len_row == 3 and ',' in sep:
            vec = row['Price'].copy(deep=True)
        elif len_row == 6 and ',' in sep:
            vec = row['Price'].copy(deep=True)
        elif len_row == 6 and ';' in sep:
            vec = row['Close'].copy(deep=True)

        row.drop(row.columns[[0]], axis=1, inplace=True)
        return vec, row, time

    def loadFile(self):
        if self.files_index > self.files_count:
            self.data.append(None)
            self.raw.append(None)
            self.time.append(None)
            return
        if self.time_mode == 'daily':
            tmp_data, tmp_raw, tmp_time = self.getStockDataVec(self.files[self.files_index])
            if self.logger:
                self.logger._add(self.files[self.files_index], "data_"+self.mode)
            self.data.append(tmp_data)
            self.raw.append(tmp_raw)
            self.time.append(tmp_time)
        elif self.time_mode == 'month':
            self.data.append(self.cmonth[self.files_index][0])
            self.raw.append(self.cmonth[self.files_index][1])
            self.time.append(self.cmonth[self.files_index][2])
        self.files_index += 1

    def concatAll(self):
        tmp_data = None
        tmp_raw = None
        tmp_time = None
        for file in range(self.files_count):
            data, raw, time = self.getStockDataVec(self.files[file])
            if tmp_data is None and tmp_time is None and tmp_raw is None:
                tmp_data = data
                tmp_raw = raw
                tmp_time = time
            else:
                tmp_data = tmp_data.append(data, ignore_index=True)
                tmp_raw = tmp_raw.append(raw, ignore_index=True)
                tmp_time = tmp_time.append(time, ignore_index=True)
        self.data.append(tmp_data)
        self.raw.append(tmp_raw)
        self.time.append(tmp_time)
        self.files_count = 1
        self.files_index = 1

    def concatPerMonth(self):
        tmp_data = None
        tmp_raw = None
        tmp_time = None
        self.files_count = 0
        for month in self.files_month:
            idx = 0
            while idx < month:
                data, raw, time = self.getStockDataVec(self.files[idx])
                if tmp_data is None and tmp_time is None and tmp_raw is None:
                    tmp_data = data
                    tmp_raw = raw
                    tmp_time = time
                else:
                    tmp_data = tmp_data.append(data, ignore_index=True)
                    tmp_raw = tmp_raw.append(raw, ignore_index=True)
                    tmp_time = tmp_time.append(time, ignore_index=True)
                if self.logger:
                    self.logger._add(self.files[idx], "data_"+self.mode)
                idx += 1
            self.files_count += 1
            self.cmonth.append([tmp_data, tmp_raw, tmp_time])

    def loadHistorical(self):
        ''' data loading from api on start '''
        historical = self.api.getHistorical()
        ticks = []
        for tick in historical:
            tick[0] = datetime.fromtimestamp(tick[0]).strftime("%Y%m%d%H%M%S")
            ticks.append([tick[0], tick[4], tick[5]])
        ticks = self.formatTo1M(pd.DataFrame(ticks, columns=self.columns))
        tick = (ticks.iloc[-self.data_max_len:]).reset_index(drop=True)
        self.raw_ticks = tick
        self.ticks = tick.join(self.indics.build_indicators(tick['Price']))
        self.time.append(self.ticks['Time'].copy(deep=True))
        self.data.append(self.ticks['Price'].copy(deep=True))
        r = self.ticks.copy(deep=True)
        self.raw.append(r.drop(r.columns[[0]], axis=1))

    def loadProcessedData(self):
        ''' load data from api and add indicators if any indicator dict exists '''
        tmp_ticks, total_ticks = self.api.getTicks()
        ticks_len = len(tmp_ticks)
        idx = 0
        tmp_size = 0
        tmp_time = datetime.now().strftime("%Y%m%d%H%M%S")
        for i in range(total_ticks):
            idx = ticks_len - total_ticks + i
            tmp_size += float(tmp_ticks[idx]['size'])
        if idx > 0:
            tmp_price = round(float(tmp_ticks[idx]['price']), 2)
            self.raw_ticks = self.raw_ticks.append(pd.DataFrame([[tmp_time,
                tmp_price, tmp_size]], columns=self.columns), ignore_index=True)
        elif len(self.ticks) > 0 and idx == 0:
            tmp_price = self.ticks['Price'].iloc[-1]
            self.raw_ticks = self.raw_ticks.append(pd.DataFrame([[tmp_time,
                tmp_price, tmp_size]], columns=self.columns), ignore_index=True)
        data = self.raw_ticks.copy(deep=True)
        data = data.join(self.indics.build_indicators(data['Price']))
        self.ticks = self.ticks.append(data.iloc[-1:], ignore_index=True)
        self.ticks = (self.ticks.iloc[-self.data_max_len:]).reset_index(drop=True)
        self.raw_ticks = (self.raw_ticks.iloc[-self.data_max_len:]).reset_index(drop=True)
        self.time.append(self.ticks['Time'].copy(deep=True))
        self.data.append(self.ticks['Price'].copy(deep=True))
        r = self.ticks.copy(deep=True)
        self.raw.append(r.drop(r.columns[[0]], axis=1))

    def formatTo1M(self, data):
        tmp_f = []
        tmp_d = int(str(data['Time'].iloc[0])[11:12]) - 1
        volume = 0
        for i in range(len(data['Time'])):
            #tqdm.write(str(data['Time'].iloc[i]))
            if (tmp_d + 1) == int(str(data['Time'].iloc[i])[10:12]):
                tmp_a = []
                for c in data.columns:
                    if c == 'Volume':
                        tmp_a.append(volume)
                    else:
                        tmp_a.append(data[c].iloc[i])
                tmp_f.append(tmp_a)
                volume = 0
            elif tmp_d != int(str(data['Time'].iloc[i])[10:12]):
                loop = 0
                while int(str(data['Time'].iloc[i])[10:12]) != tmp_d % 60:
                    tmp_a = []
                    loop += 1
                    tmp_d += 1
                    for c in data.columns:
                        if c == 'Time':
                            tmp_a.append(str(int(data[c].iloc[i - 1]) + (100 * (loop % 60))))
                        elif c == 'Volume':
                            tmp_a.append(volume)
                        else:
                            tmp_a.append(data[c].iloc[i - 1])
                    tmp_f.append(tmp_a)
                    volume = 0
            #tqdm.write(str(tmp_f[len(tmp_f) - 1]))
            volume += data['Volume'].iloc[i]
            tmp_d = int(str(data['Time'].iloc[i])[10:12])
        return (pd.DataFrame(tmp_f, columns=data.columns)).reset_index(drop=True)