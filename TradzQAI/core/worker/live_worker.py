from datetime import datetime
import time

from tqdm import tqdm
tqdm.monitor_interval = 0

class Live_Worker:

    def __init__(self, env=None, agent=None):
        if env == None or agent == None:
            raise ValueError("The worker need an agent and an environnement")

        self.env = env
        self.agent = agent
        self.deterministic = False
        if "eval" == self.env.mode:
            self.determinitic = True
        self.is_working = False
        self.changed = False

    def close(self):
        self.is_working = False

    def run(self):
        self.agent.reset()
        state = self.env.reset()
        self.is_working = True
        while self.is_working:
            if datetime.now().minute % 15 != 0:
                self.changed = False
            if datetime.now().minute % 15 == 0 and not self.changed:
                self.changed = True
                action = self.agent.act(state, deterministic=self.deterministic)
                state, terminal, reward = self.env.execute(action)
                #print (state)
                if "train" == self.env.mode:
                    self.agent.observe(reward=reward, terminal=terminal)
                if terminal and self.env.mode == "train":
                    self.agent.save_model(directory=self.env.saver.model_file_path,
                        append_timestep=True)
                if self.agent.should_stop() or self.env.stop:
                    break
            time.sleep(1)

