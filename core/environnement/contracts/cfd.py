from ..base import Wallet, Inventory

class CFD(object):

    def __init__(self):
        self.wallet = Wallet()
        self.inventory = Inventory()

        self.wallet.settings['fee'] = 0

        self.contract_settings = dict(
            pip_value = 5,
            contract_price = 125,
            spread = 1,
            allow_short = True
        )

    def getContractPrice(self, price):
        return self.contract_settings['contract_price']

    def calcBidnAsk(self, price):
        return price - self.contract_settings['spread'] / 2, price + self.contract_settings['spread'] / 2

    def getSettings(self):
        return self.contract_settings

    def getInventory(self):
        return self.inventory

    def getWallet(self):
        return self.wallet
