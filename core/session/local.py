from core import Local_Worker, Local_env
from threading import Thread

from tools import *
import time


class Local_session(Thread):

    def __init__(self, mode="train", gui=0, contract_type="classic", config='config/', db=None, agent="PPO"):
        self.db = db
        if not "/" in config[len(config)-1]:
            raise ValueError("You forget \"/\" at the end, it should be {}/".format(config))
        self.env = Local_env(mode=mode, gui=gui, contract_type=contract_type, config=config, agent=agent)
        self.config = config
        self.agent = None
        self.worker = Local_Worker
        Thread.__init__(self)

    def stop(self):
        self.env.close()

    def getWorker(self):
        return self.worker

    def getEnv(self):
        return self.env

    def getAgent(self):
        return self.agent

    def setAgent(self, agent=None, device=None):
        if agent:
            self.env.model_name = agent
        if self.env.model_name in self.env.agents:
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore",category=FutureWarning)
                self.agent = getattr(__import__('agents'), self.env.model_name)
                self.device = device
        else:
            raise ValueError('could not import %s' %self. env.model_name)

    def loadSession(self):
        if not self.env.stop:
            self.initAgent()
            self.initWorker()
        else:
            print (red("Warning : ")+"You cannot load the session without setting,\
            any data directory in %s/environnement" % self.config)

    def initAgent(self):
        if not self.agent:
            self.setAgent()
        for classe in self.agent.__mro__:
            if ("tensorforce" and self.agent.__name__) in str(classe):
                self.agent = self.agent(env=self.env, device=self.device)._get()
                return
        self.agent = self.agent(env=self.env, device=self.device)

    def initWorker(self):
        self.worker = self.worker(env=self.env, agent=self.agent)

    def run(self):
        if not self.agent:
            raise ValueError("add an agent and load the session before running")
        elif not self.env.stop:
            self.env.logger.start()
            if self.env.gui == 0:
                Thread(target=self.worker.run).start()
            else:
                self.worker.start()
        else:
            print (red("Warning : ")+"You cannot start the session without setting,\
            any data directory in %s/environnement" % self.config)
