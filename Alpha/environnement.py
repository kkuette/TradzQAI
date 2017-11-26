class environnement():

    def __init__(self):

        self.data = None
        self.data_path = "./dataset/"
        self.period = 10

        self.stock_name = ""
        self.episode_count = 100
        self.contract_price = 5
        self.max_order = 5
        self.spread = 1
        self.window_size = 50
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
        self.win = 0
        self.loose_r = 0
        self.mode = ""
