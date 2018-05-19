from .agent import Agent

class DDPG(Agent):

    def __init__(self, env=None, device=None):
        Agent.__init__(self, env=env, device=device)

    def get_specs(env=None):
        specs = {
            "type": "ddpg_agent",

            "update_mode": {
                "unit": "timesteps",
                "batch_size": env.batch_size,
                "frequency": 64
            },

            "states_preprocessing":{
                "type":"flatten",
                "shape":env.state.shape
            },

            "memory": {
                "type": "replay",
                "capacity": 100000,
                "include_next_states": True
            },

            "optimizer": {
                "type": "adam",
                "learning_rate": 1e-4
            },

            "discount": 0.99,
            "entropy_regularization": None,

            "critic_network": {
                "size_t0": 64,
                "size_t1": 64
            },

            "critic_optimizer": {
                "type": "adam",
                "learning_rate": 1e-3
            },

            "target_sync_frequency": 1,
            "target_update_weight": 0.999,

            "actions_exploration": {
                "type": "ornstein_uhlenbeck",
                "sigma": 0.3,
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
            },

            "execution": {
                "type": "single",
                "session_config": None,
                "distributed_spec": None
            }
        }
        return specs
