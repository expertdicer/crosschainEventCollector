class MemoryStorage:
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if MemoryStorage.__instance == None:
            MemoryStorage()
        return MemoryStorage.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if MemoryStorage.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            MemoryStorage.__instance = self
        self.storage = {}

    def set(self, key, value):
        self.storage[key] = value

    def get(self, key):
        return self.storage.get(key)

    def get_keys(self):
        return self.storage.keys()
