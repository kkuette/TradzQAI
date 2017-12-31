# TradzQAI

This project contains GUI for monitoring behaviour and/or backtesting trading agent (or algorithms) on a trading env, and some RL agent like DQN agent.

TradzQAI has been inspired by q-trader.
Indicators lib come from [pyti](https://github.com/kylejusticemagnuson/pyti)

More datasets available [here](http://www.histdata.com/download-free-forex-data/?/ascii/1-minute-bar-quotes)

## Status

    Alpha in development
        Working agent : DQN, DDQN, DRQN, DDRQN
        Not working agent : EIIE, DDPG

## Getting Started

  All this project run with python 3

- Dependencies :
  - [Keras](https://github.com/keras-team/keras) (with [Tensorflow](https://github.com/tensorflow/tensorflow) backend)
  - Pandas
  - Numpy
  - PyQt5
  - [pyqtgraph](https://github.com/pyqtgraph/pyqtgraph)
  
- Running the project
  ```
  py run.py
  ```
  
- Building indicators
    
    It build : RSI, MACD, VOLATILITY, EMA20, EMA50, EMA100

  - In [build.py](https://github.com/kkuette/TradzQAI/blob/master/build.py)
  
    change :   ```row_path = "../dataset/DAX30/1M", new_path = "./data/DAX30_full_wi.csv```
             
    To :     ```row_path = "your_dataset_directory_path", new_path = "your_file_path.csv" ```
           
    and run : ```py build.py```
 
## Relevant project
  - [TradingBrain](https://github.com/Prediction-Machines/Trading-Brain)
  - [Keras-rl](https://github.com/matthiasplappert/keras-rl)
  - [q-trader](https://github.com/edwardhdlu/q-trader)
 
## References
  - [DQN](https://arxiv.org/abs/1312.5602)
  - [DRQN](https://arxiv.org/abs/1507.06527)
  - [DDQN](https://arxiv.org/abs/1509.06461)
  - [DDPG](https://arxiv.org/abs/1509.02971)
  - [EIIE](https://arxiv.org/abs/1706.10059) [Official code for paper](https://github.com/ZhengyaoJiang/PGPortfolio)
  - https://keon.io/deep-q-learning/
