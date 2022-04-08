from utils.boolean_utils import to_bool
from configs.perfomance_config import PerformanceConfig


class MemoryStoragePerformance:
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if MemoryStoragePerformance.__instance == None:
            MemoryStoragePerformance()
        return MemoryStoragePerformance.__instance

    def __init__(self):
        """ Virtually private constructor. """
        self.calculate_performance = to_bool(PerformanceConfig.CALCULATE_PERFORMANCE)
        if MemoryStoragePerformance.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            MemoryStoragePerformance.__instance = self
        self.storage = {}

    def set(self, key, value):
        if not self.calculate_performance:
            return 0
        self.storage[key] = value

    def get(self, key):
        if not self.calculate_performance:
            return 0
        return self.storage.get(key)

    def set_calculate_performance(self, calculate_performance=True):
        self.calculate_performance = calculate_performance

    def get_calculate_performance(self):
        return self.calculate_performance

    def get_keys(self):
        return self.storage.keys()
