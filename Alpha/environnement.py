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
        self.window_size = 20
        self.total_profit = 0
        self.reward = 0
        self.profit = 0
        self.buy_price = 0
        self.sell_price = 0
        self.pause = 0
        self.corder = ""
        self.cdata = 0
        self.inventory = None
        self.POS_BUY = -1
        self.POS_SELL = -1
