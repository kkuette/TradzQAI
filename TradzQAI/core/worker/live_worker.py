from datetime import datetime

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

    def close(self):
        self.is_working = False

    def run(self):
        self.agent.reset()
        state = self.env.reset()
        self.is_working = True
        current_time = datetime.now().minute
        current_day = datetime.now().day
        while self.is_working:
            if current_time != datetime.now().minute:
                current_time = datetime.now().minute
                action = self.agent.act(state, deterministic=self.deterministic)
                state, terminal, reward = self.env.execute(action)
                if datetime.now().day != current_day:
                    terminal = True
                    self.env.episode_process()
                if "train" == self.env.mode:
                    self.agent.observe(reward=reward, terminal=terminal)
                if terminal and self.env.mode == "train":
                    self.agent.save_model(directory=self.env.saver.model_file_path,
                        append_timestep=True)
                if terminal:
                    self.agent.reset()
                    state = self.env.reset()
                if self.agent.should_stop() or self.env.stop:
                    break

