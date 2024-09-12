from collections import Counter
from base_model import model


class majority_class_model(model):
    def __init__(self, labels):
        counter = Counter()
        for label in labels:
            counter[label] += 1
        self.majority_class = counter.most_common(1)[0]

    def predict(self, sentence: str):
        return self.majority_class


if __name__ == "__main__":
    from read_data import train_label
    mcm = majority_class_model(train_label)
    print(mcm.predict("test sentence"))
