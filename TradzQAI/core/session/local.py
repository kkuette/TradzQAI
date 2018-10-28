from TradzQAI.core import Local_Worker, Local_env
from TradzQAI.core.environnement.base import dataLoader
from TradzQAI.tools import Saver, Logger, red

import time, os
from threading import Thread


class Local_session(Thread):

    def __init__(self, mode="train", contract_type="classic", config='config/', db=None, agent="PPO"):
        self.db = db
        if not "/" in config[len(config)-1]:
            raise ValueError("You forget \"/\" at the end, it should be {}/".format(config))
    
        self.env = None
        self.mode = mode
        self.contract_type = contract_type
        self.config = config
        self.agent = None
        self.worker = None

        self.saver = Saver()
        self.logger = None
        self.dl = None

        self.settings = dict()

        if self.saver.check_settings_files(config):
            self.settings['env'], self.settings['agent'], self.settings['network'] = self.saver.load_settings(config)
            self.saver._check(self.settings['agent']['type'].split('_')[0].upper(), self.settings)
            self.logger = Logger()
            self.dl = dataLoader(directory=self.settings['env']['base']['data_directory'], mode=self.mode)
        else:
            self.initEnv()
            default_env, default_network = self.env.get_default_settings()
            self.saver.save_settings(default_env,
                getattr(__import__('TradzQAI'), agent).get_specs(), 
                default_network, config)

        Thread.__init__(self)

    def stop(self):
        self.env.close()
        self.logger.stop()

    def getWorker(self):
        return self.worker

    def getEnv(self):
        return self.env

    def getAgent(self):
        return self.agent

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

    def loadSession(self):
        if not self.env:
            self.initEnv()
        if not self.env.stop:
            self.initAgent()
            self.initWorker()
        else:
            print (red("Warning : ")+"You cannot start the session without setting, "+\
            "any data directory in {}environnement".format(self.config))

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
        self.agent = self.agent(env=self.env, device=self.device)._get()

    def initWorker(self):
        self.worker = Local_Worker(env=self.env, agent=self.agent)

    def initEnv(self):
        self.env = Local_env(mode=self.mode, 
            contract_type=self.contract_type, config=self.settings, 
            logger=self.logger, saver=self.saver, dataloader=self.dl)

    def run(self):
        if not self.agent:
            raise ValueError("add an agent and load the session before running")
        elif not self.env.stop:
            self.logger.start()
            Thread(target=self.worker.run).start()
        else:
            print (red("Warning : ")+"You cannot start the session without setting, "+\
            "any data directory in {}environnement".format(self.config))
            self.stop()
