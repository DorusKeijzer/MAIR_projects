from abc import ABC, abstractmethod
from collections import Counter


class Model(ABC):
    """All models inherit from this class so we have a uniform way of calling them. Models implement __init__ and a predict function"""

    @abstractmethod
    # initializes the model
    def __init__(self, data: list, labels: list):
        self.name = "Model"
        pass

    @abstractmethod
    # predicts based on the sentence
    def predict(self, sentence: str) -> str:
        pass


class MajorityClassModel(Model):
    """Calculates the majority class upon initialization and always predicts this class when predicting"""

    def __init__(self, data, labels):
        self.name = "Majority class model"
        # counts how often each label occurs
        counter = Counter(labels)
        # stores the most common class
        self.majority_class = counter.most_common(1)[0][0]

    # predicts the majority class regardless of input
    def predict(self, sentence: str):
        return self.majority_class


if __name__ == "__main__":
    # tests the mcm model
    from read_data import train_label, train_data
    mcm = MajorityClassModel(train_data, train_label)
    print(mcm.predict("test sentence"))
