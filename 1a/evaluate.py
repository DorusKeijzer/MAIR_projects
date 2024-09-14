from read_data import test_data_bow as test_data, test_label, train_data_bow as train_data, train_label, vectorizer
from models import Model, MajorityClassModel, RuleBasedModel  # import each model here


def precision(model: Model, data, labels):
    """Returns the precision of the model on the given dataset."""
    correct = 0
    total = 0
    
    for sentence, label in zip(data, labels):
        # If the model is RuleBasedModel, convert the BoW vector back to text
        if isinstance(model, RuleBasedModel):
            sentence = " ".join(vectorizer.inverse_transform(sentence)[0])
        
        prediction = model.predict(sentence)
        if prediction == label:
            correct += 1
        total += 1
    
    return correct / total


if __name__ == "__main__":
    # Initialize each model here
    mcm = MajorityClassModel(train_data, train_label)
    rbm = RuleBasedModel(train_data, train_label)

    models = [mcm, rbm]  # Add more models here so they get evaluated

    # Evaluate the precision for each model
    for model in models:
        print(f"Accuracy of {model.name}: {precision(model, test_data, test_label)}")
