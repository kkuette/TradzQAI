from tensorforce.agents import Agent as Agents
import os

class Agent(object):

    def __init__(self, env=None, device=None):
        self.env = env
        if self.env.saver.model_file_name == "":
            try:
                self.env.saver.model_file_name = self.env.model_name + "_" + self.env.dataDirectory.replace("/", "")
            except:
                self.env.saver.model_file_name = self.env.model_name + "_" + self.env.dataDirectory.replace("/", "")
            if not os.path.exists(self.env.saver.model_directory+ "/model"):
                os.mkdir(self.env.saver.model_directory+ "/model")
            self.env.saver.model_file_path = self.env.saver.model_directory + "/model/" + self.env.saver.model_file_name



        self.agent = Agents.from_spec(
            self.env.settings['agent'],
            kwargs=dict(
                states=self.env.states,
                actions=dict(type='int', num_actions=self.env.actions),
                network=self.env.settings['network'],
                device=device
            )
        )

        try:
            self.agent.restore_model(self.env.saver.model_directory+"/model")
        except:
            pass

    def _get(self):
        return self.agent
