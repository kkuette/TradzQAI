from .base_env import Environnement

class Local_Env(Environnement):

    def __init__(self):
        Environnement.__init__(self)

        # Local environnement settings

        self.stock_name = "DAX30_1M_2017_10_wi2"
        self.model_dir = self.model_name + "_" + self.stock_name.split("_")[0]
        self.episode_count = 100

        # Local wallet settings

        self.spread = 1
        self.pip_value = 5
        self.contract_price = 125

        # date

        self.day = 1
        self.tot_day = 1

        self.month = 1
        self.tot_month = 1

        self.year = 1
        self.tot_year = 1
