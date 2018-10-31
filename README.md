# TradzQAI

Trading environnement for RL agents, backtesting and training.

Live session with [coinbasepro-python](https://github.com/danpaquin/coinbasepro-python) is finaly arrived !

- Available sessions:
    - Local
        - 1M bar datasets any size.
            - header should be ['Time', 'Open', 'High', 'Low', 'Close', 'Volume'] with ';' as separator
        - Tick datasets any size.
            - header should be ['Time', 'BID', 'ASK', 'VOL'] or ['Time', 'Price', 'Volume'] with ',' as separator
    - Live
        - Gdax API

- Available agents:
    - DDPG
    - DQFD
    - DQN
    - DQNN
    - NAF
    - PPO
    - TRPO
    - VPG

- Available contract type:
    - CFD
    - Classic

TradzQAI has been inspired by q-trader.

Indicators lib come from [pyti](https://github.com/kylejusticemagnuson/pyti)

More datasets available [here](http://www.histdata.com/download-free-forex-data/)

## Status

    Alpha in development
        GUI rework on track

## Getting Started

- Dependencies :
  - [Tensorflow](https://github.com/tensorflow/tensorflow)
  - [Tensorforce](https://github.com/reinforceio/tensorforce)
  - [coinbasepro-python](https://github.com/danpaquin/coinbasepro-python)
  - Pandas
  - Numpy
  - tqdm
  - h5py

  ### Installation :
    ```pip install -r requirements.txt```

- Running the project
  ```
  Usage:
    python run.py -h (Show usage)
    python run.py -b agent_name (to manually build config file, it build config files from agent, default PPO)
    python run.py -s live (for live session) 
    python run.py -m eval (for eval mode)
    python run.py -c config_dir/ # load config from directory, make sure you have agent, env and network json files in it
    python run.py (Run as default)
  ```
  When you run it for the first time, a config directory is created, you can change it to changes environnement settings and some agents settings.
  It save settings (env, agent, network) in a save directory, and create a new directory if make any changes.
  
  - Do you own decision function for maker side.
    For more info look at [this function](https://github.com/kkuette/TradzQAI/blob/master/API/api.py#L41)
    ```python
    from core import Local_session as Session
    from mymodule import myfunc
    session = Session(mode=args.mode, config=args.config)
    session.initApi(key=key, b64=b64, passphrase=passphrase, url=url,
            product_id=product_id)
    session.getApi().setBestPriceFunc(myfunc)
     ```

  - Do your own runner.
  ```python
  from core import Local_session as Session
  session = Session() # Run with default values
  session.loadSession() # loading environnement, worker and agent
  session.start() # Start the session thread
  ```
  - Do your own worker.
  ```python
  from core import Local_env
  env = Local_env() # run with default values
  for e in episode:
    state = env.reset()
    for s in step:
      action = agent.act(state)
      next_state, terminal, reward = env.execute(action)
      agent.observe(reward, terminal)
      if terminal or env.stop:
        break
    if env.stop or e == episode - 1:
      env.logger._running = False #Close the logger thread
      break
  ```
  - How to use networks.
    - You have to define your input to fit with columns name of your datasets, it will automaticaly it grab input from network and compare it with your dataset columns in [getState](https://github.com/kkuette/TradzQAI/blob/master/tools/utils.py#L326) function, it allow you to do complex network like this :
        ```json
        [
            [
                {"names": ["Price"], "type": "input"},
                {"activation": "relu", "size": 8, "type": "dense"},
                {"activation": "relu", "size": 8, "type": "dense"},
                {"name": "pricenet", "type": "output"}
            ],
            [
                {"names": ["Volume"], "type": "input"},
                {"activation": "relu", "size": 8, "type": "dense"},
                {"activation": "relu", "size": 8, "type": "dense"},
                {"name": "volnet", "type": "output"}
            ],
            [
                {"names": ["pricenet", "volnet"], "type": "input"},
                {"activation": "relu", "size": 64, "type": "dense"},
                {"activation": "relu", "size": 32, "type": "dense"},
                {"activation": "relu", "size": 8, "type": "dense"},
                {"name": "prediction", "type": "output"}
            ]
        ]
        ```

      - Simple network are handled as well without defining any input:
      ```json
        [
            {"activation": "relu", "size": 64, "type": "dense"},
            {"activation": "relu", "size": 64, "type": "dense"}
        ]
        ```
  - Also TradzQAI support pre trained keras model:
    - You can build settings for your model by using ```py run.py -b DEEP```.
    Your model have to be placed in the same directory as the one you use to launch it and have to be called ```deep_model.h5```.

        

## Relevant project
  - [TradingBrain](https://github.com/Prediction-Machines/Trading-Brain)
  - [q-trader](https://github.com/edwardhdlu/q-trader)
  
### This project isn't perfect so keep this in mind.
```THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.```
