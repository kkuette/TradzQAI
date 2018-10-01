from .agent import Agent

class NAF(Agent):

    def __init__(self, env=None, device=None):
        Agent.__init__(self, env=env, device=device)

    def get_specs(env=None):
        specs = {
            "type": "naf_agent",

            "update_mode": {
                "unit": "timesteps",
                "batch_size": 64,
                "frequency": 4
            },

            "memory": {
                "type": "replay",
                "capacity": 10000,
                "include_next_states": True
            },

            "optimizer": {
                "type": "adam",
                "learning_rate": 1e-3
            },

            "discount": 0.99,
            "entropy_regularization": False,
            "double_q_model": True,

            "target_sync_frequency": 1000,
            "target_update_weight": 1.0,

            "actions_exploration": {
                "type": "ornstein_uhlenbeck",
                "sigma": 0.2,
                "mu": 0.0,
                "theta": 0.15
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
