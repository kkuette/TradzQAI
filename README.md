# TradzQAI

This project contains GUI for monitoring behaviour and/or backtesting trading agent (or algorithms), some RL agent like DQN agent and indicators lib.

TradZQAI has been inspired by q-trader, and indicators lib come from [pyti](https://github.com/kylejusticemagnuson/pyti)

## Status

    Alpha in development

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
 
## Sources
  - https://arxiv.org/abs/1312.5602 for DQN
  - https://arxiv.org/abs/1509.06461 for DDQN
  - https://keon.io/deep-q-learning/
