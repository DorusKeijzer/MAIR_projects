from abc import ABC, abstractmethod


class Model(ABC):
    """All models inherit from this class so we have a uniform way of calling them. Models implement __init__ and a predict function"""

    @abstractmethod
    def __init__(self, data: list, labels: list):
        self.name = "Model"
        pass

    @abstractmethod
    def predict(self, sentence: str) -> str:
        pass
