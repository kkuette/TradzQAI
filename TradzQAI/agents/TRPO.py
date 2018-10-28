class TRPO:

    def __init__(self, env=None, device=None):
        Agent.__init__(self, env=env, device=device)

    def get_specs(env=None):
        specs = {
            "type": "trpo_agent",

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

            "learning_rate": 1e-2,

            "discount": 0.99,
            "entropy_regularization": None,
            "gae_lambda": None,
            "likelihood_ratio_clipping": None,

            "baseline_mode": None,
            "baseline":  None,
            "baseline_optimizer": None,

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
