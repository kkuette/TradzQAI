from .agent import Agent

class VPG(Agent):

    def __init__(self, env=None, device=None):
        Agent.__init__(self, env=env, device=device)

    def get_specs(env=None):
        specs = {
            "type": "vpg_agent",

            "update_mode": {
                "unit": "episodes",
                "batch_size": 20,
                "frequency": 20
            },

            "memory": {
                "type": "latest",
                "include_next_states": False,
                "capacity": 5000
            },

            "optimizer": {
                "type": "adam",
                "learning_rate": 2e-2
            },

            "discount": 0.99,
            "entropy_regularization": None,
            "gae_lambda": None,

            "baseline_mode": "states",

            "baseline": {
                "type": "mlp",
                "sizes": [32, 32]
            },

            "baseline_optimizer": {
                "type": "multi_step",
                "optimizer": {
                    "type": "adam",
                    "learning_rate": 1e-3
                    },
                "num_steps": 5
            },

            "saver": {
                "directory": None,
                "seconds": 600
            },

            "summarizer": {
                "directory": None,
                "labels": [],
                "seconds": 120
            },

            "execution": {
                "type": "single",
                "session_config": None,
                "distributed_spec": None
            }
        }
        return specs
