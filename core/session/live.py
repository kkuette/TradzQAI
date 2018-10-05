from core import Live_Worker, Live_env
from API import Api
from threading import Thread
import datetime

class Live_session(Thread):

    def __init__(self, mode="train", gui=0, contract_type="classic",
            config='config/', db=None, agent="PPO"):

        self.db = db
        if not "/" in config[len(config)-1]:
            raise ValueError("You forget \"/\" at the end, it should be {}/".format(config))
        self.env = None
        self.agent = None
        self.api = None
        self.api_name = None
        self.env_mode = mode
        self.gui = gui
        self.contract_type = contract_type
        self.config = config
        self.worker = Live_Worker
        Thread.__init__(self)

    def stop(self):
        self.worker.close()
        self.api.close()
        self.env.close()

    def getWorker(self):
        return self.worker

    def getEnv(self):
        return self.env

    def getAgent(self):
        return self.agent

    def getApi(self):
        return self.api

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
            raise ValueError('could not import %s' %self.env.model_name)

    def setApi(self, api_name="cbpro"):
        self.api_name = api_name

    def loadSession(self):
        if not self.env:
            self.initEnv()
        if not self.env.stop:
            self.initAgent()
            if not self.api:
                self.initApi()
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

    def initApi(self, key=None, b64=None, passphrase=None, url=None,
            product_id=['BTC-EUR'], mode="maker", auto_cancel=True):
        if not self.api_name:
            self.setApi()
        self.api = Api(api_name=self.api_name, key=key, b64=b64,
            passphrase=passphrase, url=url, product_id=product_id, mode=mode,
            auto_cancel=auto_cancel)
        self.initEnv()

    def initEnv(self):
        self.env = Live_env(mode=self.env_mode, gui=self.gui,
            contract_type=self.contract_type, config=self.config, api=self.api)

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
