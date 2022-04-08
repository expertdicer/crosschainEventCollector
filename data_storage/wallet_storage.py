class WalletMemoryStorage:
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if WalletMemoryStorage.__instance == None:
            WalletMemoryStorage()
        return WalletMemoryStorage.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if WalletMemoryStorage.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            WalletMemoryStorage.__instance = self
        self.storage = {}

    def set(self, key, value):
        self.storage[key] = value

    def get(self, key):
        return self.storage.get(key)

    def get_keys(self):
        return self.storage.keys()


class WalletInMemory:
    def __init__(self):
        self.balance = {}
        self.deposit = {}
        self.borrow = {}
        self.update_checkpoint = 0
