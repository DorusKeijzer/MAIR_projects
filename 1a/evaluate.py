from read_data import (
    test_sentences, test_label, train_sentences, train_label,
    train_data_bow, dedup_train_data_bow, unique_train_sentences, unique_train_labels,
    vectorizer
)
from models import (
    Model, MajorityClassModel, RuleBasedModel, DecisionTreeModel, 
    LogisticRegressionModel, FeedForwardNNModel
)

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

def evaluate_model(model: Model, data, labels, label_set):
    """Evaluates the model and prints detailed metrics."""
    predictions = []
    for sentence in data:
        predictions.append(model.predict(sentence))
    
    # Compute overall accuracy
    accuracy = accuracy_score(labels, predictions)
    print(f"Accuracy of {model.name}: {accuracy:.2%}")
    
    # Compute precision, recall, F1-score per class
    report = classification_report(labels, predictions, labels=label_set, zero_division=0)
    print(f"Classification Report for {model.name}:\n{report}")
    
    # Compute confusion matrix
    cm = confusion_matrix(labels, predictions, labels=label_set)
    print(f"Confusion Matrix for {model.name}:\n{cm}")
    
    return predictions, accuracy, report, cm

if __name__ == "__main__":
    # Get the set of labels
    label_set = sorted(set(train_label))

    # Initialize the models with the original training data
    print("Evaluating models with original data:")
    mcm_orig = MajorityClassModel(train_sentences, train_label)  # Majority Class Model
    rbm_orig = RuleBasedModel(train_sentences, train_label)  # Rule-Based Model
    dtm_orig = DecisionTreeModel(train_data_bow, train_label)  # Decision Tree Model
    lrm_orig = LogisticRegressionModel(train_data_bow, train_label)  # Logistic Regression Model
    ffnn_orig = FeedForwardNNModel(train_data_bow, train_label)  # Feed Forward NN Model

    models_orig = [mcm_orig, rbm_orig, dtm_orig, lrm_orig, ffnn_orig]

    # Store predictions from all models
    all_model_predictions = {}

    # Evaluate each model
    for model in models_orig:
        print(f"\nEvaluating {model.name} with original data:")
        predictions, accuracy, report, cm = evaluate_model(model, test_sentences, test_label, label_set)
        all_model_predictions[model.name] = predictions

    # Error analysis: identify difficult sentences (misclassified by most models)
    print("\nIdentifying difficult sentences misclassified by most models:")
    misclassification_counts = {}
    for idx, sentence in enumerate(test_sentences):
        true_label = test_label[idx]
        misclassified_by = []
        for model_name, predictions in all_model_predictions.items():
            if predictions[idx] != true_label:
                misclassified_by.append(model_name)
        if len(misclassified_by) > 0:
            misclassification_counts[sentence] = {
                'true_label': true_label,
                'misclassified_by': misclassified_by
            }

    # Find sentences misclassified by the most models
    difficult_sentences = sorted(
        misclassification_counts.items(),
        key=lambda x: len(x[1]['misclassified_by']),
        reverse=True
    )

    # Print out the top difficult sentences
    print("\nTop difficult sentences misclassified by most models:")
    for i, (sentence, info) in enumerate(difficult_sentences[:5]):  # Adjust the number as needed
        print(f"{i+1}. Sentence: '{sentence}'")
        print(f"   True label: {info['true_label']}")
        print(f"   Misclassified by: {', '.join(info['misclassified_by'])}\n")

    # Now, evaluate models trained on deduplicated data for system comparison
    print("\nEvaluating models with deduplicated data:")
    # Note: MajorityClassModel and RuleBasedModel are not affected by deduplication in the same way
    # So we will focus on models that use the training data directly
    dtm_dedup = DecisionTreeModel(dedup_train_data_bow, unique_train_labels)  # Decision Tree Model
    lrm_dedup = LogisticRegressionModel(dedup_train_data_bow, unique_train_labels)  # Logistic Regression Model
    ffnn_dedup = FeedForwardNNModel(dedup_train_data_bow, unique_train_labels)  # Feed Forward NN Model

    models_dedup = [dtm_dedup, lrm_dedup, ffnn_dedup]

    for model in models_dedup:
        print(f"\nEvaluating {model.name} with deduplicated data:")
        evaluate_model(model, test_sentences, test_label, label_set)
