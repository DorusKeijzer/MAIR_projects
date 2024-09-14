from abc import ABC, abstractmethod
from collections import Counter
import re
from read_data import (
    train_data_bow, train_label, dedup_train_data_bow, unique_train_labels,
    train_sentences, test_sentences, vectorizer, OOV_INDEX, handle_oov
)

from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from keras.models import Sequential
from keras.layers import Dense
from keras.utils import to_categorical
import numpy as np

class Model(ABC):
    """All models inherit from this class so we have a uniform way of calling them. Models implement __init__ and a predict function."""

    @abstractmethod
    def __init__(self, data: list, labels: list):
        self.name = "Model"
        pass

    @abstractmethod
    def predict(self, sentence: str) -> str:
        pass

class RuleBasedModel(Model):
    """Classifies sentences based on keyword matching for each dialog act."""
    
    def __init__(self, data, labels):
        super().__init__(data, labels)
        self.name = "Rule-based model"
        self.rules = {
            "bye": ["farewell", "see you", "take care", "later"],
            "hello": ["hello", "hi", "welcome", "greetings"],
            "thankyou": ["thank you", "thanks", "much appreciated", "thank you goodbye", "thank you and goodbye", "goodbye"],
            "affirm": ["yes", "right", "correct", "absolutely", "sure", "yeah", "definitely", "indeed", "of course"],
            "negate": ["no", "not", "never", "nope", "wrong", "incorrect"],
            "request": ["could", "can", "what", "where", "how", "phone number", "address", "postcode", "location", "tell me", "type of", "phone", "i need", "please provide", "may I have", "would you", "could you", "is there a", "is this", "what is", "where is", "can you", "would you be able to"],
            "reqmore": ["more", "another", "else", "something else", "additional", "extra"],
            "reqalts": ["how about", "alternative", "else", "another", "other options", "instead", "alternatively", "other choices", "what about"],
            "inform": ["restaurant", "place", "serves", "food", "looking for", "price", "offers", "menu", "type", "part", "town", "moderately", "cheap", "north", "south", "chinese", "provides", "serves", "location", "situated", "found", "available", "details", "info", "information", "can you tell me"],
            "confirm": ["is there", "is it", "confirm", "does it", "verify", "true", "is this", "is there a", "can you confirm", "do you confirm", "is this correct", "can I confirm", "is that correct", "is that true", "can you confirm this", "is it correct", "confirm this for me"],
            "deny": ["don't want", "not this", "reject", "decline", "disagree", "no thanks", "no thank you"],
            "ack": ["okay", "ah", "kay", "alright", "got it", "okay then", "i see", "understood", "right", "uh-huh"],
            "repeat": ["repeat", "say again", "again please", "one more time", "could you repeat", "restate", "repeat that", "could you say that again"],
            "restart": ["start over", "again", "restart", "reset", "from the beginning", "restart the process", "begin again", "let's start over"],
            "null": ["noise", "unintelligible", "cough", "silence", "static", "um", "code", "unclear", "not clear", "no response", "empty", "background noise", "pause", "inaudible", "background sound"],
        }

    def predict(self, sentence: str) -> str:
        """Predict the dialog act based on the presence of keywords, ensuring word boundaries."""       
        # Check each dialog act with word boundaries
        for dialog_act, keywords in self.rules.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', sentence):
                    return dialog_act
        
        return "inform"  # Fallback to "inform" if no keywords match

class MajorityClassModel(Model):
    """Calculates the majority class upon initialization and always predicts this class when predicting."""

    def __init__(self, data, labels):
        super().__init__(data, labels)
        self.name = "Majority class model"
        counter = Counter(labels)
        self.majority_class = counter.most_common(1)[0][0]

    def predict(self, sentence: str):
        return self.majority_class

class DecisionTreeModel(Model):
    """Decision Tree classifier based on bag-of-words features."""

    def __init__(self, data, labels):
        super().__init__(data, labels)
        self.name = "Decision Tree model"
        self.model = DecisionTreeClassifier()
        self.model.fit(data, labels)

    def predict(self, sentence: str) -> str:
        # Convert the raw sentence to a bag-of-words feature vector
        sentence_bow = vectorizer.transform([sentence])
        # Predict the label using the decision tree model
        return self.model.predict(sentence_bow)[0]

class LogisticRegressionModel(Model):
    """Logistic Regression classifier based on bag-of-words features."""

    def __init__(self, data, labels):
        super().__init__(data, labels)
        self.name = "Logistic Regression model"
        self.model = LogisticRegression(max_iter=200)
        self.model.fit(data, labels)

    def predict(self, sentence: str):
        # Convert the raw sentence to a bag-of-words feature vector
        sentence_bow = vectorizer.transform([sentence])
        # Predict the label using the logistic regression model
        return self.model.predict(sentence_bow)[0]

class FeedForwardNNModel(Model):
    """Feed Forward Neural Network classifier based on bag-of-words features using Keras."""

    def __init__(self, data, labels):
        super().__init__(data, labels)
        self.name = "Feed Forward NN model"
        self.num_classes = len(set(labels))
        self.model = Sequential([
            Dense(100, activation='relu', input_shape=(data.shape[1],)),
            Dense(self.num_classes, activation='softmax')
        ])
        self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['Accuracy'])
        
        # Convert labels to categorical
        labels_categorical = to_categorical([self.label_to_index(label) for label in labels], num_classes=self.num_classes)
        self.model.fit(data, labels_categorical, epochs=10, verbose=0)  # Train model quietly

    def label_to_index(self, label):
        return list(set(train_label)).index(label)

    def index_to_label(self, index):
        return list(set(train_label))[index]

    def predict(self, sentence: str):
        # Convert the raw sentence to a bag-of-words feature vector and handle OOV
        sentence_bow = vectorizer.transform([sentence])
        prediction = self.model.predict(sentence_bow.toarray(), verbose=0)[0]  # Suppress output here
        return self.index_to_label(np.argmax(prediction))



if __name__ == "__main__":
    # Initialize the models with training data
    mcm = MajorityClassModel(train_sentences, train_label)  # Majority Class Model
    rbm = RuleBasedModel(train_sentences, train_label)  # Rule-Based Model
    dtm = DecisionTreeModel(train_data_bow, train_label)  # Decision Tree Model
    lrm = LogisticRegressionModel(train_data_bow, train_label)  # Logistic Regression Model
    ffnn = FeedForwardNNModel(train_data_bow, train_label)  # Feed Forward NN Model

    models = [mcm, rbm, dtm, lrm, ffnn]  # Add more models here so they get evaluated

    # Example usage or testing on test data
    for model in models:
        print(f"Example prediction from {model.name}: {model.predict(test_sentences[0])}")
