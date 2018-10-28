from tqdm import tqdm
tqdm.monitor_interval = 0

class Local_Worker:

    def __init__(self, env=None, agent=None):
        if not env or not agent:
            raise ValueError("The worker need an agent and an environnement")

        self.env = env
        self.agent = agent
        self.deterministic = False
        if "eval" in self.env.mode:
            self.env.episode_count = 1
            self.deterministic = True

    def run(self):
        step = tqdm(range(self.env.dl.files_count))
        for s in step:
            d = self.env.dl.files[s].split('/')
            step.set_description(desc="%s " % d[len(d) - 1], refresh=True)
            step.update(1)
            self.step()
            self.env.nextDataset()
            if self.env.stop:
                break

        if self.env.mode == "eval":
            self.env.eval_processing()
        step.close()
        self.env.close()

    def step(self):
        ep = tqdm(range(self.env.episode_count), desc="Episode Processing ")

        for e in ep:
            state = self.env.reset()
            self.agent.reset()

            dat = tqdm(range(self.env.len_data), desc="Step Processing ")
            for t in dat:
                action = self.agent.act(state, deterministic=self.deterministic) # Get action from agent
                # Get new state
                state, terminal, reward = self.env.execute(action)
                if "train" == self.env.mode:
                    self.agent.observe(reward=reward, terminal=terminal)
                dat.update(1)
                if terminal or self.agent.should_stop() or self.env.stop:
                    break

            dat.close()
            ep.update(1)
            if e == self.env.episode_count - 1:
                self.env.next = True
            if self.agent.should_stop() or self.env.stop:
                if terminal and self.env.mode == "train":
                    self.agent.save_model(directory=self.env.saver.model_file_path, append_timestep=True)
                ep.close()
                break
