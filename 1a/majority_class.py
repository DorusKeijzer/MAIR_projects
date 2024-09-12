from collections import Counter
from base_model import Model


class MajorityClassModel(Model):
    def __init__(self, data, labels):
        counter = Counter()
        for label in labels:
            counter[label] += 1
        self.majority_class = counter.most_common(1)[0][0]
        self.name = "Majority class model"

    def predict(self, sentence: str):
        return self.majority_class


if __name__ == "__main__":
    from read_data import train_label, train_data
    mcm = MajorityClassModel(train_data, train_label)
    print(mcm.predict("test sentence"))
