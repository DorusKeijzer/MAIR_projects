from read_data import test_data, test_label, train_data, train_label
from models import Model, MajorityClassModel  # import each model here


def precision(model: Model, data, labels):
    """Returns the precision of the model on the given dataset"""
    correct = 0
    total = 0
    for sentence, label in zip(data, labels):
        prediction = model.predict(sentence)
        if prediction == label:
            correct += 1
        total += 1
    return correct/total


if __name__ == "__main__":
    # initialize each model here
    mcm = MajorityClassModel(train_data, train_label)

    models = [mcm]  # add more models here so they get evaluated

    # evaluate the precision for each model
    for model in models:
        print(f"Accuracy of {model.name}: {
              precision(model, test_data, test_label)}")
