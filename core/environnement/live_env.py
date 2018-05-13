from .base.base_env import Environnement

class Live_env(Environnement):

    def __init__(self, gui, contract_type):
        Environnement.__init__(self, gui)
