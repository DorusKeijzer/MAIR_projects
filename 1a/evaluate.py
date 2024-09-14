from read_data import (
    test_sentences, test_label, train_sentences, train_label,
    train_data_bow, dedup_train_data_bow, unique_train_labels,
    vectorizer
)
from models import (
    Model, MajorityClassModel, RuleBasedModel, DecisionTreeModel, 
    LogisticRegressionModel, FeedForwardNNModel
)

def precision(model: Model, data, labels):
    """Returns the precision of the model on the given dataset."""
    correct = 0
    total = 0
    
    for sentence, label in zip(data, labels):
        prediction = model.predict(sentence)
        if prediction == label:
            correct += 1
        total += 1
    
    return correct / total

if __name__ == "__main__":
    # Initialize the models with the original training data
    print("Evaluating models with original data:")
    mcm_orig = MajorityClassModel(train_sentences, train_label)  # Majority Class Model
    rbm_orig = RuleBasedModel(train_sentences, train_label)  # Rule-Based Model
    dtm_orig = DecisionTreeModel(train_data_bow, train_label)  # Decision Tree Model
    lrm_orig = LogisticRegressionModel(train_data_bow, train_label)  # Logistic Regression Model
    ffnn_orig = FeedForwardNNModel(train_data_bow, train_label)  # Feed Forward NN Model

    models_orig = [mcm_orig, rbm_orig, dtm_orig, lrm_orig, ffnn_orig]

    # Evaluate the precision for each model using test sentences
    for model in models_orig:
        accuracy = precision(model, test_sentences, test_label)
        print(f"Precision of {model.name} with original data: {accuracy:.2%}")

    # Initialize the models with the deduplicated training data
    print("\nEvaluating models with deduplicated data:")
    dtm_dedup = DecisionTreeModel(dedup_train_data_bow, unique_train_labels)  # Decision Tree Model
    lrm_dedup = LogisticRegressionModel(dedup_train_data_bow, unique_train_labels)  # Logistic Regression Model
    ffnn_dedup = FeedForwardNNModel(dedup_train_data_bow, unique_train_labels)  # Feed Forward NN Model

    models_dedup = [dtm_dedup, lrm_dedup, ffnn_dedup]

    # Evaluate the precision for each model using the same test sentences (to ensure consistency)
    for model in models_dedup:
        accuracy = precision(model, test_sentences, test_label)
        print(f"Precision of {model.name} with deduplicated data: {accuracy:.2%}")
