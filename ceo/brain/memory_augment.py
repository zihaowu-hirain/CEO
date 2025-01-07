import abc
from collections import OrderedDict


class MemoryAugment:
    def __init__(self, memory: OrderedDict | None = None):
        self._memory: OrderedDict | None = None
        if memory is not None:
            self._memory = memory.copy()

    @property
    def memory(self) -> OrderedDict | None:
        if self._memory is not None:
            return self._memory.copy()
        return None

    @abc.abstractmethod
    def bring_in_memory(self, memory: OrderedDict):
        pass
