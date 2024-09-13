from abc import ABC, abstractmethod
from collections import Counter


class Model(ABC):
    """All models inherit from this class so we have a uniform way of calling them. Models implement __init__ and a predict function"""

    @abstractmethod
    def __init__(self, data: list, labels: list):
        self.name = "Model"
        pass

    @abstractmethod
    def predict(self, sentence: str) -> str:
        pass


class MajorityClassModel(Model):
    def __init__(self, data, labels):
        counter = Counter(labels)
        self.majority_class = counter.most_common(1)[0][0]
        self.name = "Majority class model"

    def predict(self, sentence: str):
        return self.majority_class


if __name__ == "__main__":
    from read_data import train_label, train_data
    mcm = MajorityClassModel(train_data, train_label)
    print(mcm.predict("test sentence"))
