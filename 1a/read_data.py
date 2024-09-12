import os

data_path = os.path.join("data", "dialog_acts.dat")

dataset = []

with open(data_path) as file:
    for line in file:
        line = line.split()
        label = line[0]
        sentence = line[1:]
        dataset.append((label, sentence))

print(dataset[0:10])
print(len(dataset))
