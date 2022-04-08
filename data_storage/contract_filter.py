class ContractFilterMemoryStorage:
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if ContractFilterMemoryStorage.__instance == None:
            ContractFilterMemoryStorage()
        return ContractFilterMemoryStorage.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if ContractFilterMemoryStorage.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            ContractFilterMemoryStorage.__instance = self
        self.storage = set()
        self.temp_set = set()

    def add(self, address):
        self.storage.add(address)

    def exited(self, address):
        return address in self.storage

    def add_temp(self, address):
        self.temp_set.add(address)

    def clear_temp(self):
        self.temp_set = set()

    def get_temp_set(self):
        return self.temp_set
