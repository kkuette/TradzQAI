from .agent import Agent

class PPO(Agent):

    def __init__(self, env=None, device=None):
        Agent.__init__(self, env=env, device=device)

    def get_specs(env=None):
        specs = {
            "type": "ppo_agent",

            "update_mode": {
                "unit": "episodes",
                "batch_size": 10,
                "frequency": 10
            },

            "memory": {
                "type": "latest",
                "include_next_states": False,
                "capacity": 5000
            },

            "step_optimizer": {
                "type": "adam",
                "learning_rate": 1e-3
            },

            "subsampling_fraction": 0.1,
            "optimization_steps": 50,

            "discount": 0.99,
            "entropy_regularization": 0.01,
            "gae_lambda": None,
            "likelihood_ratio_clipping": 0.2,

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
