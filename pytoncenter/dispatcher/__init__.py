from abc import ABCMeta, abstractmethod
from threading import Lock
from typing import List


class BaseKeyRotator(metaclass=ABCMeta):
    def __init__(self, keys: List[str]) -> None:
        assert isinstance(keys, list), "keys must be a list of strings"
        assert len(keys) > 0, "keys must not be empty"
        self.keys = keys

    @abstractmethod
    def get_key(self):
        raise NotImplementedError


class RoundRobinKeyRotator(BaseKeyRotator):
    def __init__(self, keys: List[str]) -> None:
        super().__init__(keys)
        self.index = 0
        self.lock = Lock()

    def get_key(self):
        with self.lock:
            key = self.keys[self.index]
            self.index = (self.index + 1) % len(self.keys)
        return key
