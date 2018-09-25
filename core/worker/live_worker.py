from tools import *

import time
import sys
import json
import datetime

from threading import Thread
from API import gdax

from tqdm import tqdm
tqdm.monitor_interval = 0

from websocket import WebSocketConnectionClosedException

from PyQt5.QtCore import *

class Live_Worker(QThread, gdax.WebsocketClient):

    sig_step = pyqtSignal()
    sig_batch = pyqtSignal()
    sig_episode = pyqtSignal()

    def __init__(self, env=None, agent=None):
        self.name = os.path.basename(__file__).replace(".py", "")

        if env == None or agent == None:
            raise ValueError("The worker need an agent and an environnement")

        #if env.gui == 0:
            #env.init_logger()
            #env.logger._save_conf(env)

        self.env = env
        self.agent = agent
        self.firstMsg = True
        self.firstData = True
        self.save_time = None
        #env.logger.new_logs(self.name)
        #env.logger._add("Initialization", self.name)
        gdax.WebsocketClient.__init__(self, url="wss://ws-feed.gdax.com", products=[self.env.stock_name],
                    channels=['ticker'], should_print=True)
        if self.env.gui == 1:
            QThread.__init__(self)

    def _start(self):
        def _go():
            self._connect()
            self._listen()
            self._disconnect()

        self.stop = False
        self.on_open()
        self.thread = Thread(target=_go)
        self.thread.start()

    def _listen(self):
        Thread(target=self.keepalive).start()
        self.agent.reset()
        self.env.start_t = time.time()
        self.save_time = time.time()
        self.env.stop = self.stop
        while not self.stop:
            try:
                data = self.ws.recv()
                msg = json.loads(data)
            except ValueError as e:
                self.on_error(e)
            except Exception as e:
                self.on_error(e)
            else:
                if self.env.stop:
                    self.stop = self.env.stop
                if 'ticker' in msg['type'] and not self.firstMsg:
                    if self.should_print:
                        print (json.dumps(msg, indent=4, sort_keys=True))
                    self.env.addData(msg)
                    self.on_message()
                else:
                    self.env.data = []
                    self.firstMsg = False

    def on_message(self):
        if self.firstData:
            self.state = self.env.reset()
            self.agent.reset()
            self.firstData = False
        tmp = time.time()
        action = self.agent.act(self.state) # Get action from agent
        # Get new state
        next_state, terminal, reward = self.env.execute(action)
        if self.should_print:
            print (self.env.wallet.settings['capital'], self.env.wallet.profit['current'],
                action, reward, terminal)
            print (str(self.env.inventory.get_inventory()))
        self.state = next_state
        if "train" in self.env.mode:
            self.agent.observe(reward=reward, terminal=terminal)
            if int((time.time() - self.save_time) / 60) >= 5:
                if self.should_print:
                    print ("Saving ", int(time.time() - self.save_time))
                self.agent._save_model()
                self.save_time = time.time()
        if self.env.gui == 1:
            self.sig_step.emit() # Update GUI
            time.sleep(0.07)
        self.env.loop_t = time.time() - tmp
        if self.should_print:
            print (self.env.loop_t)
        if terminal is True or self.agent.should_stop():
            if self.env.gui == 1:
                self.sig_episode.emit()
            self.env.start_t = time.time()
            self.firstData = True

    def on_close(self):
        if self.should_print:
            print("\n-- Socket Closed --")
            print ("Exec time {}".format(datetime.datetime.now() - self.env.exec_time))

    def run(self):
        self._start()
