from tensorforce.agents import Agent as Agents

class Agent(object):

    def __init__(self, env=None, device=None):
        self.env = env
        if self.env.saver.model_file_name == "":
            try:
                self.env.saver.model_file_name = self.env.model_name + "_" + self.env.stock_name.split("_")[0] + "_" + self.env.stock_name.split("_")[1]
            except:
                self.env.saver.model_file_name = self.env.model_name + "_" + self.env.stock_name.split("_")[0]
            self.env.saver.model_file_path = self.env.saver.model_directory + "/" + self.env.saver.model_file_name

        self.agent = Agents.from_spec(
            self.env.settings['agent'],
            kwargs=dict(
                states=dict(type='float', shape=self.env.state.shape),
                actions=dict(type='int', num_actions=self.env.actions),
                network=self.env.settings['network'],
                device=device
            )
        )

        try:
            self.agent.restore_model(self.env.saver.model_directory)
        except:
            pass

    def _get(self):
        return self.agent
