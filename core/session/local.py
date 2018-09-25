from core import Local_Worker
from core import Local_env
from threading import Thread
import time


class Local_session(Thread):

    def __init__(self, mode="train", gui=0, contract_type="classic", config='config/', db=None):
        self.db = db
        if not "/" in config[len(config)-1]:
            raise ValueError("You forget \"/\" at the end, it should be {}/".format(config))
        self.env = Local_env(mode=mode, gui=gui, contract_type=contract_type, config=config)
        self.agent = None
        self.worker = Local_Worker
        self.env.stop = False
        Thread.__init__(self)

    def _stop(self):

        self.env.stop = True
        time.sleep(2)

        try:
            self.env.logger._running = False
        except:
            pass


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
        self.initAgent()
        self.initWorker()

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
        else:
            if self.env.gui == 0:
                Thread(target=self.worker.run).start()
            else:
                self.worker.start()
