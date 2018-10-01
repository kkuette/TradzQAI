import os
from threading import Thread

class Api(Thread):

    def __init__(self, name="cbpro", key=None, b64=None,
        passphrase=None, product_id=['BTC-EUR'], db=None ):
        self.product = product_id
        if name in self.srcAPI():
            self._api = getattr(getattr(__import__('API.%s' % name), name), name+'wrapper')
        self.initAPI(key=key, b64=b64, passphrase=passphrase,
            product_id=product_id, db=db)
        Thread.__init__(self)

    def srcAPI(self):
        ignore = ['__init__.py', 'api.py', '__pycache__']
        valid = []
        for f in os.listdir("API"):
            if f not in ignore:
                valid.append(f)
        return valid

    def initAPI(self, key=None, b64=None, passphrase=None, product_id=['BTC-EUR'], db=None):
        self._api = self._api(key=key, b64=b64, passphrase=passphrase, product_id=product_id, db=db)

    def getAPI(self):
        return self._api

    def buy(self, volume):
        self._api.havetobuy = True
        self._api.order_size = volume

    def sell(self, volume):
        self._api.havetosell = True
        self._api.order_size = volume

    def run(self):
        self._api.run()
