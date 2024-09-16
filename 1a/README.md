This repository contains the code to train and evaluate several models. `read_data.py` reads the input sentences and stores them as bag-of-word feature vectors, `models.py` contains the model architectures, `train.py` trains the models and stores their weights in `model_weights/`, `evaluate.py` evaluates the models on several metrics. 

# read_data.py
The Python Script file uses "sklearn.feature_extraction.text" to convert the given dataset to token counts and "sklearn.model_selection " to get the train and test split.

First, we append labels and sentences to read the given data set. Then, we split the dataset as instructed using "sklearn.model_selection "- 85% train and 15% test. We use zip to combine train sentences and train labels and eventually, de-duplicate the training dataset. Using the "sklearn.feature_extraction.text", we create bag-of-words vectorizer based on the original training sentences.

FUNCTION [handle_oov]: For out-of-vocabulary (OOV) words, we created a function to handle them and tokenize them as zero.

Then, we export the variables needed for model training and evaluation.





# running the program

if you are using conda:

```bash
cd 1a
conda create -n "MAIR_group_16" python
conda activate "MAIR_group_16"
pip install -r requirements.txt
python evaluate.py
```

if this fails, the repo also contains a dockerfile that allows you to build and run a docker container.
```bash
cd 1a
docker build -t models .
docker run --name models .

```


