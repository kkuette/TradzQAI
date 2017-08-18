import numpy as np
from RNN import *


l = np.array([[['1','2','3'],['4','5','6'],['7','8','9']],[['10','12','13'],['14','15','16'],['17','18','19']]])


new = RNN()
new.path = "dataset/DAX30/dax30_2017_01/DAT_ASCII_GRXEUR_M1_201701.csv"
new.get_data()
