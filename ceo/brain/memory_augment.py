import abc


class MemoryAugment:
    def __init__(self, memory: dict | None = None):
        self._memory = memory

    @property
    def memory(self) -> dict:
        return self._memory

    @abc.abstractmethod
    def bring_in_memory(self, memory: dict):
        pass
