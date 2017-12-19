from core import environnement
from agents import DQN
from tools import *

if __name__ == '__main__':
    env = environnement()
    a, d = getStockDataVec(env.stock_name)
    D = DQN(getState(d, 0, env.window_size), env=env)
    D._save_model()
