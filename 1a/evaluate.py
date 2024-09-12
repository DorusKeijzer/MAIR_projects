from read_data import test_data, test_label, train_data, train_label
from majority_class import MajorityClassModel
from base_model import Model


def precision(model: Model, data, labels):
    correct = 0
    total = 0
    for sentence, label in zip(data, labels):
        prediction = model.predict(sentence)
        if prediction == label:
            correct += 1
        total += 1
    return correct/total


if __name__ == "__main__":

    mcm = MajorityClassModel(train_data, train_label)

    models = [mcm]  # add more models here
    for model in models:
        print(f"Accuracy of {model.name}: {
              precision(model, test_data, test_label)}")
