from .agent import Agent

class DQN(Agent):

    def __init__(self, env=None, device=None):
        Agent.__init__(self, env=env, device=device)

    def get_specs(env=None):
        specs = {
            "type": "dqn_agent",

            "states_preprocessing": {
                "type":"flatten"
            },

            "update_mode": {
                "unit": "timesteps",
                "batch_size": 32,
                "frequency": 1
            },

            "memory": {
                "type": "replay",
                "capacity": 10000,
                "include_next_states": True
            },

            "optimizer": {
                "type": "clipped_step",
                "clipping_value": 0.1,
                "optimizer": {
                    "type": "adam",
                    "learning_rate": 1e-3
                }
            },

            "discount": 0.97,
            "entropy_regularization": None,

            "actions_exploration": {
                "type": "epsilon_decay",
                "initial_epsilon": 1.0,
                "final_epsilon": 0.0,
                "timesteps": 10000
            },

            "saver": {
                "directory": None,
                "seconds": 600
            },

            "summarizer": {
                "directory": None,
                "labels": [],
                "seconds": 120
            }
            }
        return specs
