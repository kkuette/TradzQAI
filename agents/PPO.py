from .agent import Agent

class PPO(Agent):

    def __init__(self, env=None, device=None):
        Agent.__init__(self, env=env, device=device)

    def get_specs(env=None):
        specs = {
            "type": "ppo_agent",

            "actions_exploration":{
                "type": "epsilon_anneal",
                "initial_epsilon": 1.0,
                "final_epsilon": 0.1,
            },

            "update_mode": {
                "unit": "episodes",
                "batch_size": 32,
                "frequency": 32
            },

            "step_optimizer": {
                "type": "adam",
                "learning_rate": 3e-3
            },

            "discount": 0.97,

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
