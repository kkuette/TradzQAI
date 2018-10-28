import os

class Agent(object):

    def __init__(self, env=None, device=None):
        ''' Wrapper agent class '''

        self.env = env
        if not self.env.settings['agent']['type'] == "DEEP":
            # Hide TF loading logs
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            from tensorforce.agents import Agent as Agents
            # Check if there is any existing model for this config
            # Make directory if config doesn't exist
            if self.env.saver.model_file_name == "":
                try:
                    self.env.saver.model_file_name = self.env.model_name
                except:
                    self.env.saver.model_file_name = self.env.model_name
                if not os.path.exists(self.env.saver.model_directory+ "/model"):
                    os.mkdir(self.env.saver.model_directory+ "/model")
                self.env.saver.model_file_path = self.env.saver.model_directory + "/model/" + self.env.saver.model_file_name

            # Load agent from current config
            self.agent = Agents.from_spec(
                self.env.settings['agent'],
                kwargs=dict(
                    states=self.env.states,
                    actions=dict(type='int', num_actions=self.env.actions),
                    network=self.env.settings['network'],
                    device=device
                )
            )
            # Load agent if it already exists
            try:
                self.agent.restore_model(self.env.saver.model_directory+"/model")
            except:
                pass
        else:
            from .DEEP import DEEP
            # Load deep learning model (keras model), only work with eval mode
            self.agent = DEEP("deep_model.h5")

    def _get(self):
        ''' Return current agent '''
        return self.agent
