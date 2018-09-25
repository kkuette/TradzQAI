from core import Live_Worker
from core import Live_env
from threading import Thread
import keyboard
import datetime

class Live_session(Thread):

    def __init__(self, mode="train", gui=0, contract_type="classic", config='config/', db=None):
        self.db = db
        if not "/" in config[len(config)-1]:
            raise ValueError("You forget \"/\" at the end, it should be {}/".format(config))
        self.env = Live_env(mode=mode, gui=gui, contract_type=contract_type, config=config)
        self.env.exec_time = datetime.datetime.now()
        self.agent = None
        self.worker = Live_Worker
        self.env.stop = False
        keyboard.add_hotkey('ctrl+c', self._stop)
        Thread.__init__(self)

    def _stop(self):
        self.env.stop = True

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
                self.agent = getattr(__import__("agents", fromlist=[self.env.model_name]), self.env.model_name)
                self.device = device
        else:
            raise ValueError('could not import %s' %self. env.model_name)

    def loadSession(self):
        self.initAgent()
        self.initWorker()

    def initAgent(self):
        if not self.agent:
            self.setAgent()
        self.agent = self.agent(env=self.env, device=self.device)

    def initWorker(self):
        self.worker = self.worker(env=self.env, agent=self.agent)

    def run(self):
        if not self.agent:
            raise ValueError("add an agent and load the session before running")
        else:
            self.worker.run()
