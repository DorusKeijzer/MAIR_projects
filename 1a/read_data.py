import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split

data_path = "../data/dialog_acts.dat"

labels = []
sentences = []

# reads files and writes the labels
# and sentences to their respective lists
with open(data_path) as file:
    for line in file:
        line = line.split()
        labels.append(line[0])

        sentence = " ".join(line[1:])
        sentences.append(sentence)

# creates bag of words embeddings
vectorizer = CountVectorizer()
vectorizer.fit(sentences)

# applies embedding transformation to each sentence in the dataset
bag_of_words = vectorizer.transform(sentences)

# splits the data into 15% test data and 85% training data
train_data, test_data, train_label, test_label = train_test_split(
    bag_of_words, labels, test_size=0.15)

if __name__ == "__main__":
    # prints a few sentences and embeddings for debugging purposes
    print(f"sentences: {sentences[0:10]}")
    print(f"labels: {labels[0:10]}")
    print(f"bag of words: {train_data[0:10]}")
