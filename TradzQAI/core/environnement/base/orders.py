class orders:

    def __init__(self):
        ''' Order storage and build class '''
        self.orders = {}
        self._id = -1

    def get_order(self, _id):
        return self.orders[str(_id)]

    def _close(self, _id=None):
        self.orders.pop(str(_id))

    def _open(self, price, side, size, fee):
        self._id += 1
        # init order
        self.orders[self._id] = order(_id=self._id)
        # create and return an order
        return self.orders[self._id](price, side, size, fee)

    def __call__(self, price, side, size, fee):
        return self._open(price, side, size, fee)

class order:

    def __init__(self, _id=None):
        ''' 
        Order class
            args:
                _id: (int) order id
        '''

        self.price = None
        self.side = None
        self.size = None
        self.fee = None
        self.started = None
        self._id = _id

    def __call__(self, price, side, size, fee):
        self.price = price
        self.side = side
        self.size = size
        self.fee = fee
        return self

    def __repr__(self):
        return "{}(id={}, side={}, price={}, size={}, fee={})".format(\
            self.__class__.__name__,
            self._id,
            self.side,
            self.price,
            self.size,
            self.fee)