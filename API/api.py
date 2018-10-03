import os

class Api(object):

    def __init__(self, api_name="cbpro", key=None, b64=None,
        passphrase=None, product_id=['BTC-EUR'], db=None,
        url="https://api.pro.coinbase.com", mode="maker"):

        self.mode = mode
        self.key = key
        self.b64 = b64
        self.passphrase = passphrase
        self.db = db
        self.url = url
        self.product_id = product_id

        self.setAPI(api_name=api_name)
        self.initAPI()

    def srcAPI(self):
        ignore = ['__init__.py', 'api.py', '__pycache__']
        valid = []
        for f in os.listdir("API"):
            if f not in ignore:
                valid.append(f)
        return valid

    def initAPI(self):
        self._api = self._api(key=self.key, b64=self.b64, passphrase=self.passphrase,
            product_id=self.product_id, db=self.db, url=self.url, mode=self.mode)

    def setAPI(self, api_name=None):
        if api_name:
            self.api_name = api_name
        if self.api_name in self.srcAPI():
            self._api = getattr(getattr(__import__('API.%s' % self.api_name),
                self.api_name), self.api_name+'wrapper')

    def setBestPriceFunc(self, func):
        """
            Set a function for any strategy.

            args:
                last bids: function that take a int (depth)
                        return: <generator> each row is a list filled with dict
                last asks: function that take a int (depth)
                        return: <generator> each row is a list filled with dict
        """
        self._api.setBestPriceFunc(func)

    def getAPI(self):
        return self._api

    def buy(self, volume):
        self._api.addOrder("buy", volume)

    def sell(self, volume):
        self._api.addOrder("sell", volume)

    def stop(self):
        self._api.stop()

    def start(self):
        self._api.run()
