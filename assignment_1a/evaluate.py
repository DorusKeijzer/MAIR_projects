# evaluate.py

from read_data import (
    test_sentences, test_label, train_sentences, train_label,
    train_data_bow, dedup_train_data_bow, unique_train_labels,
    vectorizer
)
from models import (
    Model, MajorityClassModel, RuleBasedModel, DecisionTreeModel,
    LogisticRegressionModel, FeedForwardNNModel
)

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import os

def evaluate_model(model: Model, data, labels, label_set):
    """Evaluates the model and prints detailed metrics."""
    if hasattr(model, 'predict_batch'):
        print(f"Using batch prediction for {model.name}")
        predictions = model.predict_batch(data)
    else:
        print(f"Using individual predictions for {model.name}")
        predictions = [model.predict(sentence) for sentence in data]

    # Check if all predictions are in label_set
    unique_predictions = set(predictions)
    unknown_predictions = unique_predictions - set(label_set)
    if unknown_predictions:
        raise ValueError(f"Classification metrics can't handle a mix of multiclass and unknown targets: {unknown_predictions}")

    # Compute overall accuracy
    accuracy = accuracy_score(labels, predictions)
    print(f"Accuracy of {model.name}: {accuracy:.2%}")

    # Compute precision, recall, F1-score per class
    report = classification_report(
        labels, predictions, labels=label_set, zero_division=0
    )
    print(f"Classification Report for {model.name}:\n{report}")

    # Compute confusion matrix
    cm = confusion_matrix(labels, predictions, labels=label_set)
    print(f"Confusion Matrix for {model.name}:\n{cm}")

    return predictions, accuracy, report, cm

if __name__ == "__main__":
    # Initialize any required variables
    all_model_predictions = {}

    # Get the set of labels
    label_set = sorted(set(train_label))

    # Initialize the models with the original training data
    print("Evaluating models with original data:")
    mcm_orig = MajorityClassModel(train_sentences, train_label)  # Majority Class Model
    rbm_orig = RuleBasedModel(train_sentences, train_label)      # Rule-Based Model
    dtm_orig = DecisionTreeModel(train_data_bow, train_label, data_type='normal')  # Decision Tree Model
    lrm_orig = LogisticRegressionModel(train_data_bow, train_label, data_type='normal')  # Logistic Regression Model
    ffnn_orig = FeedForwardNNModel(train_data_bow, train_label, data_type='normal')  # Feed Forward NN Model

    models_orig = [mcm_orig, rbm_orig, dtm_orig, lrm_orig, ffnn_orig]

    # Handle training and weight saving/loading for original data models
    for model in models_orig:
        print(f"\nEvaluating {model.name} with original data:")
        if hasattr(model, 'weights_path') and os.path.exists(model.weights_path):
            # Load existing weights
            model.load_weights()
            print(f"Loaded weights for {model.name}")
        else:
            # Train the model and save weights
            if hasattr(model, 'train'):
                print(f"Training {model.name}")
                model.train()
                if hasattr(model, 'save_weights'):
                    # Ensure the directory exists
                    weights_dir = os.path.dirname(model.weights_path)
                    if not os.path.exists(weights_dir):
                        os.makedirs(weights_dir)
                    model.save_weights()
                    print(f"Saved weights for {model.name}")
        # Evaluate the model
        try:
            predictions, accuracy, report, cm = evaluate_model(
                model, test_sentences, test_label, label_set
            )
            # Store predictions for error analysis, excluding models that do not require it
            if model.name not in ['Majority class model', 'Rule-based model']:
                all_model_predictions[model.name] = predictions
        except ValueError as ve:
            print(f"Error evaluating {model.name}: {ve}")

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
    # Adjust the number as needed
    for i, (sentence, info) in enumerate(difficult_sentences[:5]):
        print(f"{i+1}. Sentence: '{sentence}'")
        print(f"   True label: {info['true_label']}")
        print(f"   Misclassified by: {', '.join(info['misclassified_by'])}\n")

    # Now, evaluate models trained on deduplicated data for system comparison
    print("\nEvaluating models with deduplicated data:")
    # Initialize models with deduplicated data and specify data_type='dedup'
    dtm_dedup = DecisionTreeModel(dedup_train_data_bow, unique_train_labels, data_type='dedup')
    lrm_dedup = LogisticRegressionModel(dedup_train_data_bow, unique_train_labels, data_type='dedup')
    ffnn_dedup = FeedForwardNNModel(dedup_train_data_bow, unique_train_labels, data_type='dedup')

    models_dedup = [dtm_dedup, lrm_dedup, ffnn_dedup]

    # Handle training and weight saving/loading for deduplicated data models
    for model in models_dedup:
        print(f"\nEvaluating {model.name} with deduplicated data:")
        if hasattr(model, 'weights_path') and os.path.exists(model.weights_path):
            # Load existing weights
            model.load_weights()
            print(f"Loaded weights for {model.name}")
        else:
            # Train the model and save weights
            if hasattr(model, 'train'):
                print(f"Training {model.name}")
                model.train()
                if hasattr(model, 'save_weights'):
                    # Ensure the directory exists
                    weights_dir = os.path.dirname(model.weights_path)
                    if not os.path.exists(weights_dir):
                        os.makedirs(weights_dir)
                    model.save_weights()
                    print(f"Saved weights for {model.name}")
        # Evaluate the model
        try:
            predictions, accuracy, report, cm = evaluate_model(
                model, test_sentences, test_label, label_set
            )
            # Optionally, store these predictions if needed for further analysis
        except ValueError as ve:
            print(f"Error evaluating {model.name}: {ve}")
