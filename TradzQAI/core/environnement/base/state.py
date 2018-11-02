import numpy as np

import TradzQAI.tools

class state:

    def __init__(self, window, preprocessing=None, valid_columns=None, mode='local'):
        ''' 
        State class for data formating

            args:
                window: (int) size of array
                preprocessing: (str) how each row are processed
                valid_columns: (list) list of valid data columns that are returned
                mode: (str) local or live for index management

            return: When called
                state: (array)
        '''
        self.window = window + 1
        self.mode = mode
        
        if not hasattr(TradzQAI.tools, preprocessing):
            raise ValueError("{} does not exists.".format(preprocessing))
        self.preprocessing = getattr(TradzQAI.tools, preprocessing)
        self.valid_columns = valid_columns

        self.index = -1

    def reset(self):
        self.index = -1

    def getBlock(self, tmp, col):
        ''' 
        getBlock

            args:
                tmp: (numpy array) from a pandas dataframe columns
                col: (str) columns name
            return:
                numpy array of a columns from a pandas dataframe
        '''
        d = self.index - self.window + 1
        block = tmp[d:self.index + 1] if d >= 0 else np.concatenate(\
            [-d * [tmp[0]]] + [tmp[0:self.index + 1]])
        res = []
        for i in range(self.window - 1):
            if ("Price" or "EMA") in col:
                res.append(self.preprocessing(block[i + 1] - block[i]))
            else:
                res.append(block[i + 1])
        return np.array(res)

    def getState(self, data):
        '''
        getState
            n-time state representation ending at time window
            args: 
                data: (pandas dataframe)
            return:
                numpy array or dict of numpy array
        '''
        datas = dict()
        temp = []
        for col in data.columns:
            if self.valid_columns:
                if col in self.valid_columns:
                    res = self.getBlock(np.asarray(data[col]), col)
                    datas[col] = np.array(res)
            else:
                res = self.getBlock(np.asarray(data[col]), col)
                temp.append(res)
        if not self.valid_columns:
            datas = []
            for idx in range(len(temp[0])):
                datas.append([temp[i][idx] for i in range(len(data.columns))])
            datas = np.array(datas)
        elif 'Indics' in self.valid_columns:
            i = -1
            ind = []
            for col in data.columns:
                if not ('Price' or 'Volume') in col:
                    res = self.getBlock(np.asarray(data[col]), col)
                    temp.append(res)
                    i += 1
            for idx in range(len(temp[0])):
                ind.append([temp[v][idx] for v in range(i)])
            datas['Indics'] = np.array(ind)
        return datas

    def __call__(self, data, data_len=0):
        if self.mode == 'local':
            self.index += 1
        else:
            self.index = data_len - 1
        return self.getState(data)
