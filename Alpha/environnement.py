class environnement():

    def __init__(self):

        self.data = None
        self.data_path = "./dataset/"
        self.period = 10

        self.act = ""
        self.stock_name = "dax30_2017_10"
        self.episode_count = 100
        self.contract_price = 5
        self.max_order = 20
        self.spread = 1
        self.window_size = 100
        self.total_profit = 0
        self.reward = 0
        self.profit = 0
        self.buy_price = 0
        self.sell_price = 0
        self.pause = 0
        self.corder = ""
        self.cdata = 0
        self.cdatai = 0
        self.inventory = None
        self.POS_BUY = -1
        self.POS_SELL = -1
        self.cd = 0 
        self.co = ""
        self.win = 0
        self.loose = 0
        self.draw = 0
        self.mode = ""

        # Time var
        self.start_t = 0
        self.loop_t = 0

        # List for graph building

        ## Overview list

        self.lst_order = []
        self.lst_inventory_len = []
        self.lst_profit = []
        self.lst_data = []

        ## model list

        self.lst_act = []
        self.lst_reward = []
        self.lst_act_predit = []
        self.lst_traget_predict = []
        self.lst_target = []
        self.lst_state = []
        self.lst_epsilon = []

        ## Historical list

    def def_act(self, act):
        if act == 1:
            self.act = "BUY"
            self.lst_act.append(1)
        elif act == 2:
            self.act = "SELL"
            self.lst_act.append(-1)
        else:
            self.act = "HOLD"
            self.lst_act.append(0)
