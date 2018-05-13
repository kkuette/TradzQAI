from ..base import wallet, inventory

class CFD(object):

    def __init__(self):
        self.wallet = Wallet()
        self.inventory = Inventory()

    def getInventory(self):
        return self.inventory

    def getWallet(self):
        return self.wallet
