import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split


# Get the directory of the current file (read_data.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the data file
data_path = os.path.join(current_dir, "data", "dialog_acts.dat")


labels = []
sentences = []

# Read the file and split each line into label and sentence
with open(data_path) as file:
    for line in file:
        label, sentence = line.split(maxsplit=1)
        labels.append(label)
        sentences.append(sentence.strip())

# Split the original dataset into 85% training and 15% test data (unvectorized sentences)
train_sentences, test_sentences, train_label, test_label = train_test_split(
    sentences, labels, test_size=0.15, random_state=42)

# Deduplicate the training dataset
unique_train_sentences = []
unique_train_labels = []
seen_train = set()

for sentence, label in zip(train_sentences, train_label):
    if sentence not in seen_train:
        seen_train.add(sentence)
        unique_train_sentences.append(sentence)
        unique_train_labels.append(label)

# Create bag-of-words vectorizer based on the original training sentences
vectorizer = CountVectorizer()
vectorizer.fit(train_sentences)

# Create bag-of-words embeddings for the original training data
train_data_bow = vectorizer.transform(train_sentences)

# Create bag-of-words embeddings for the deduplicated training data
dedup_train_data_bow = vectorizer.transform(unique_train_sentences)

# Special integer for out-of-vocabulary (OOV) words
OOV_INDEX = 0

# Function to handle OOV words for new input


def handle_oov(sentence, vectorizer, oov_index=OOV_INDEX):
    tokens = sentence.split()
    indices = []
    for token in tokens:
        if token in vectorizer.vocabulary_:
            indices.append(vectorizer.vocabulary_[token])
        else:
            # Assign OOV index for out-of-vocabulary words
            indices.append(oov_index)
    return indices


# Export the variables needed for model training and evaluation
__all__ = [
    'train_data_bow', 'train_label', 'dedup_train_data_bow', 'unique_train_labels',
    'train_sentences', 'test_sentences', 'train_label', 'test_label',
    'vectorizer', 'OOV_INDEX', 'handle_oov'
]

if __name__ == "__main__":
    # Print out the first few entries for debugging purposes
    print(f"Original Sentences: {len(train_label)
                                 } training, {len(test_label)} testing")
    print(f"Deduplicated Sentences: {len(unique_train_labels)} training")
    print(f"Vectorized Original Training Data (first 10 rows):\n{
          train_data_bow[:10].toarray()}")
    print(f"Vectorized Deduplicated Training Data (first 10 rows):\n{
          dedup_train_data_bow[:10].toarray()}")
