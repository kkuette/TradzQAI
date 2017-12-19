from tools import *

import pandas as pd

if __name__ == '__main__':
    row_path = "../dataset/DAX30/1M"
    new_path = "./data/DAX30_full_wi.csv"
    data = get_all_data(row_path)
    data.to_csv(new_path, sep = ';', mode= 'w')
