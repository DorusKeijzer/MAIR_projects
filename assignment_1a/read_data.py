import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from collections import Counter
from joblib import dump

# Get the directory of the current file (read_data.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the data file
data_path = os.path.join(current_dir, "data", "dialog_acts.dat")

labels = []
sentences = []

# Read the file and split each line into label and sentence
with open(data_path, encoding='utf-8') as file:
    for line_number, line in enumerate(file, start=1):
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2:
            label, sentence = parts
            labels.append(label)
            sentences.append(sentence.strip())
        else:
            print(f"Skipping malformed line {line_number}: {line.strip()}")

# Split the original dataset into 85% training and 15% test data (unvectorized sentences)
train_sentences, test_sentences, train_label, test_label = train_test_split(
    sentences, labels, test_size=0.15, random_state=42, stratify=labels)

# Deduplicate the training dataset while ensuring at least one sentence per label
unique_train_sentences = []
unique_train_labels = []
seen_train = set()

# Step 1: Retain one unique sentence per label
labels_seen = set()
for sentence, label in zip(train_sentences, train_label):
    if label not in labels_seen and sentence not in seen_train:
        unique_train_sentences.append(sentence)
        unique_train_labels.append(label)
        seen_train.add(sentence)
        labels_seen.add(label)

# Step 2: Deduplicate the remaining data
for sentence, label in zip(train_sentences, train_label):
    if sentence not in seen_train:
        unique_train_sentences.append(sentence)
        unique_train_labels.append(label)
        seen_train.add(sentence)

# Verification: Ensure all labels are retained
missing_labels = set(train_label) - set(unique_train_labels)
if missing_labels:
    print(f"Warning: The following labels are missing in deduplicated training data: {missing_labels}")
    # Optionally, handle missing labels by adding dummy sentences or adjusting deduplication logic
else:
    print("All labels are present in deduplicated training data.")

# Create bag-of-words vectorizer based on the original training sentences
vectorizer = CountVectorizer()
vectorizer.fit(train_sentences)

# Save the fitted vectorizer to disk
vectorizer_path = os.path.join(current_dir, "model_weights", "vectorizer.joblib")
dump(vectorizer, vectorizer_path)
print(f"Vectorizer saved to {vectorizer_path}")

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
    'train_sentences', 'test_sentences', 'test_label',  # Removed duplicate 'train_label'
    'vectorizer', 'OOV_INDEX', 'handle_oov'
]

if __name__ == "__main__":
    # Print out the first few entries for debugging purposes
    print(f"Original Sentences: {len(train_label)} training, {len(test_label)} testing")
    print(f"Deduplicated Sentences: {len(unique_train_labels)} training")
    print(f"Vectorized Original Training Data (first 10 rows):\n{train_data_bow[:10].toarray()}")
    print(f"Vectorized Deduplicated Training Data (first 10 rows):\n{dedup_train_data_bow[:10].toarray()}")

    # Additional Debugging: Check if all labels are present
    print("\nLabel Distribution in Original Training Data:")
    original_label_counts = Counter(train_label)
    for label, count in original_label_counts.items():
        print(f"  {label}: {count}")

    print("\nLabel Distribution in Deduplicated Training Data:")
    dedup_label_counts = Counter(unique_train_labels)
    for label, count in dedup_label_counts.items():
        print(f"  {label}: {count}")
