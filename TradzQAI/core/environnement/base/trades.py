from . import orders

class trades:

    def __init__(self):
        ''' Trade storage and build class '''
        self.current = None
        self.last = None
        self._id = -1
        self.historical = {}
        self.loose = 0
        self.win = 0
        self.draw = 0   

    def get_trade(self, _id):
        return self.historical[str(_id)]

    def __call__(self):
        self._id += 1
        if self._id > 1:
            self.last = self.historical[str(self._id - 1)]
        # init trade
        self.historical[str(self._id)] = trade(self._id)
        self.current = self.historical[str(self._id)]
        return self.current

class trade:

    def __init__(self, _id):
        ''' 
        Trade class
            args:
                _id: (int) order id
        '''
        self.open = None
        self.close = None
        self._id = _id
        self.pnl = 0
        self.fees = 0

    def __call__(self, order):
        if not self.open:
            self.open = order
        else:
            self.close = order
            self.fees = self.open.fee + self.close.fee
            if self.open.side == 'sell':
                r = (self.open.price * self.open.size) - \
                    (self.close.price * self.close.size)
            else:
                r = (self.close.price - self.close.size) - \
                    (self.open.price * self.open.size)
            self.pnl = r + self.fees

    def __repr__(self):
        return "{}(id={}, open={}, close={}, pnl={}, fees={})".format(
                        self.__class__.__name__,
                        self._id,
                        self.open,
                        self.close,
                        self.pnl,
                        self.fees
                        )