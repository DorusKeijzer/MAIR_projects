<<<<<<< HEAD
import os
import sys
=======
>>>>>>> 46ee73298c232a702241eee9cf1031b6c2ea5f6d
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
print(os.getcwd())
print("Python executable path:", sys.executable)
print("Environment location:", sys.prefix)
data_path = "DorusKeijzer/MAIR_projects/data/dialog_acts.dat"

<<<<<<< HEAD
=======
# Load the data
data_path = "1a/dialog_acts.dat"

>>>>>>> 46ee73298c232a702241eee9cf1031b6c2ea5f6d
labels = []
sentences = []

# Read the file and split each line into label and sentence
with open(data_path) as file:
    for line in file:
        label, sentence = line.split(maxsplit=1)
        labels.append(label)
        sentences.append(sentence.strip())

# Create bag-of-words embeddings
vectorizer = CountVectorizer()
bag_of_words = vectorizer.fit_transform(sentences)

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
            indices.append(oov_index)  # Assign OOV index for out-of-vocabulary words
    return indices

# Split the data into 85% training and 15% test data
train_data_bow, test_data_bow, train_label, test_label = train_test_split(
    bag_of_words, labels, test_size=0.15, random_state=42)

train_sentences, test_sentences = train_test_split(
    sentences, test_size=0.15, random_state=42)

# Export the variables for use in other scripts
__all__ = ['train_data_bow', 'test_data_bow', 'train_label', 'test_label', 
           'train_sentences', 'test_sentences', 'vectorizer', 'OOV_INDEX', 'handle_oov']

if __name__ == "__main__":
    # Print out the first few entries for debugging purposes
    print(f"Sentences: {train_sentences[:10]}")
    print(f"Labels: {train_label[:10]}")
    print(f"Bag of words: {train_data_bow[:10].toarray()}")
