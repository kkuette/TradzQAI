from ..base import Wallet, Inventory

class Classic(object):

    def __init__(self):
        self.wallet = Wallet()
        self.inventory = Inventory()

        self.contract_settings = dict(
            pip_value = 1,
            contract_price = 0,
            spread = 0.1,
            allow_short = False
        )

    def getContractPrice(self, price):
        return price

    def calcBidnAsk(self, price):
        return price - self.contract_settings['spread'] / 2, price + self.contract_settings['spread'] / 2

    def calcSpread(self, bid, ask):
        return ask - bid

    def getSettings(self):
        return self.contract_settings

    def getInventory(self):
        return self.inventory

    def getWallet(self):
        return self.wallet
