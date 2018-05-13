from ..base import Wallet, Inventory

class Classic(object):

    def __init__(self):
        self.wallet = Wallet()
        self.inventory = Inventory()

    def getInventory(self):
        return self.inventory

    def getWallet(self):
        return self.wallet
