import psutil

class MemoryManager:

    __instance = None

    @staticmethod
    def getInstance():
        if MemoryManager.__instance == None:
            MemoryManager()
        return MemoryManager.__instance

    def __init__(self, memory_limit_percentage: float = None):
        if MemoryManager.__instance == None:
            if memory_limit_percentage == None:
                self.max_memory = None
            else:
                self.max_memory = 4096 * 1024 * 1024 * memory_limit_percentage * 0.97
                print("Using {:.0f} MB of memory".format(self.max_memory/0.97/1024/1024))
            self.pid = psutil.Process()
            MemoryManager.__instance = self
        else:
            raise Exception("This class is a singleton!")

    def can_afford_memory(self, memory: int = 0):
        if self.max_memory == None:
            return self.pid.memory_info().rss + memory < psutil.virtual_memory().available
        return self.pid.memory_info().rss + memory < self.max_memory
    
    def get_memory_usage(self):
        return self.pid.memory_info().rss

