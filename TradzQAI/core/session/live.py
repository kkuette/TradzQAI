from TradzQAI.core import Live_Worker, Live_env
from TradzQAI.API import Api
from TradzQAI.core.environnement.base import dataLoader
from TradzQAI.tools import Saver, Logger, red

from threading import Thread
import datetime, os

class Live_session(Thread):

    def __init__(self, mode="train", contract_type="classic",
            config='config/', db=None, agent="PPO"):

        self.db = db
        if not "/" in config[len(config)-1]:
            raise ValueError("You forget \"/\" at the end, it should be {}/".format(config))
        self.env = None
        self.mode = mode
        self.contract_type = contract_type
        self.config = config
        self.agent = None
        self.worker = None
        self.api_name = None

        self.saver = Saver()
        self.logger = None
        self.dl = None

        self.settings = dict()

        if self.saver.check_settings_files(config):
            self.settings['env'], self.settings['agent'], self.settings['network'] = self.saver.load_settings(config)
            self.logger = Logger()
        else:
            self.initEnv()
            default_env, default_network = self.env.get_default_settings()
            self.saver.save_settings(default_env,
                getattr(__import__('TradzQAI'), agent).get_specs(), 
                default_network, config)
        Thread.__init__(self)

    def stop(self):
        if self.worker:
            self.worker.close()
        self.logger.stop()
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
        if self.settings['agent']['type'].split('_')[0].upper() in self.src_agents():
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore",category=FutureWarning)
                from TradzQAI.agents.agent import Agent
                self.agent = Agent
                self.device = device
        else:
            raise ValueError('could not import %s' % self.settings['agent']['type'].split('_')[0].upper())

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

    def src_agents(self):
        ignore = ['Agent.py', '__init__.py', '__pycache__']
        valid = []
        for f in os.listdir("TradzQAI/agents"):
            if f not in ignore:
                valid.append(f.replace(".py", ""))
        return valid

    def initAgent(self):
        if not self.agent:
            self.setAgent()
        for classe in self.agent.__mro__:
            if ("tensorforce" and self.agent.__name__) in str(classe):
                self.agent = self.agent(env=self.env, device=self.device)._get()
                return
        self.agent = self.agent(env=self.env, device=self.device)

    def initWorker(self):
        self.worker = Live_Worker(env=self.env, agent=self.agent)

    def initApi(self, key=None, b64=None, passphrase=None, url=None,
            product_id=['BTC-EUR'], mode="maker", auto_cancel=True):
        if not self.api_name:
            self.setApi()
        self.api = Api(api_name=self.api_name, key=key, b64=b64,
            passphrase=passphrase, url=url, product_id=product_id, mode=mode,
            auto_cancel=auto_cancel)  
        self.dl = dataLoader(mode=self.mode, api=self.api)
        del self.settings['env']['base']['data_directory']
        self.saver._check(self.settings['agent']['type'].split('_')[0].upper(), self.settings)
        self.initEnv()

    def initEnv(self):
        self.env = Live_env(mode=self.mode, 
            contract_type=self.contract_type, config=self.settings, 
            logger=self.logger, saver=self.saver, dataloader=self.dl, api=self.api)

    def run(self):
        if not self.agent:
            raise ValueError("add an agent and load the session before running")
        elif not self.env.stop:
            self.env.logger.start()
            Thread(target=self.worker.run).start()
        else:
            print (red("Warning : ")+"You cannot start the session without setting,\
            any data directory in %s/environnement" % self.config)
