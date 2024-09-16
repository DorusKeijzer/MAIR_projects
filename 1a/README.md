This repository contains the code to train and evaluate several models. `read_data.py` reads the input sentences and stores them as bag-of-word feature vectors, `models.py` contains the model architectures, `train.py` trains the models and stores their weights in `model_weights/`, `evaluate.py` evaluates the models on several metrics. 

# read_data.py
The Python Script file uses "sklearn.feature_extraction.text" to convert the given dataset to token counts and "sklearn.model_selection " to get the train and test split.

First, we append labels and sentences to read the given data set. Then, we split the dataset as instructed using "sklearn.model_selection "- 85% train and 15% test. We use zip to combine train sentences and train labels and eventually, de-duplicate the training dataset. Using the "sklearn.feature_extraction.text", we create bag-of-words vectorizer based on the original training sentences.

FUNCTION [handle_oov]: For out-of-vocabulary (OOV) words, we created a function to handle them and tokenize them as zero.

Then, we export the variables needed for model training and evaluation.

# models.py
The Python Script file uses modules such as abc, collections, re, sklearn, keras, numpy, and joblib. Module abc offers a an approach to define abstract base classes. Module collections provides different container data types. Re module is used for regular expression matching. sklearn Module is used for Machine Learning model purposes - Decision Tree Classifier, Logistic Regression, and Base Estimator. Keras has been used for a stack of layers. Numpy module has been used for its computational power. And, joblib module has been used for its optimiaztion power around serialization.

CLASS [Model] All models inherit from this class so we have a uniform way of calling them. It implements init and a predict function.

CLASS [RuleBasedModel] This class classifies sentences based on keyword matching for each dialog act.

CLASS [MajorityClassModel] This class calculates the majority class upon initialization and always predicts this class when predicting.

CLASS [ScikitModel] This class is the base class for models using scikit-learn classifiers.

CLASS [DecisionTreeModel] This class is a decision Tree classifier based on bag-of-words features.

CLASS [LogisticRegressionModel] This class is a logistic Regression classifier based on bag-of-words features.

CLASS [FeedForwardNNModel] This class is Feed Forward Neural Network classifier based on bag-of-words features using Keras.

Then, we initialize the models with training data.

# train_models.py
The Python Script file uses the read_data.py and models.py script files to train the models.





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


