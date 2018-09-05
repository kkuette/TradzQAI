from .agent import Agent

class DQFD(Agent):

    def __init__(self, env=None, device=None):
        Agent.__init__(self, env=env, device=device)

    def get_specs(env=None):
        specs = {
            "type": "dqfd_agent",

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
            "entropy_regularization": None,

            "target_sync_frequency": 1000,
            "target_update_weight": 1.0,

            "actions_exploration": {
                "type": "epsilon_decay",
                "initial_epsilon": 0.5,
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
            },

            "execution": {
                "type": "single",
                "session_config": None,
                "distributed_spec": None
            }
        }
        return specs
