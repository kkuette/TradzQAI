from core.worker import Live_Worker
from core.environnement import Live_env
from threading import Thread

class Live_session(Thread):

    def __init__(self, gui, contract_type, db=None):
        raise NotImplementedError
        self.db = db
        self.env = Live_env(gui, contract_type)
        self.agent = None
        self.worker = Live_Worker
        Thread.__init__(self)

    def getWorker(self):
        return self.worker

    def getEnv(self):
        return self.env

    def getAgent(self):
        return self.agent

    def addAgent(self, agent, device=None):
        self.agent = agent
        self.device = device

    def loadSession(self):
        self.initAgent()
        self.initWorker()

    def initAgent(self):
        if not self.agent:
            raise ValueError("No agent added")
        self.agent = self.agent(env=self.env, device=self.device)

    def initWorker(self):
        self.worker = self.worker(env=self.env, agent=self.agent)

    def run(self):
        if not self.agent:
            raise ValueError("add an agent and load the session before running")
        else:
            self.worker.run()
