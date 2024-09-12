import os
from sklearn.feature_extraction.text import CountVectorizer

data_path = os.path.join("../data", "dialog_acts.dat")

labels = []
sentences = []

with open(data_path) as file:
    for line in file:
        line = line.split()
        labels.append(line[0])

        sentence = " ".join(line[1:])
        sentences.append(sentence)

vectorizer = CountVectorizer()
vectorizer.fit(sentences)

bag_of_words = vectorizer.transform(sentences)

dataset = list(zip(labels, bag_of_words))

if __name__ == "__main__":
    print(dataset)
