This repository contains the code to train and evaluate several models. `read_data.py` reads the input sentences and stores them as bag-of-word feature vectors, `models.py` contains the model architectures, `train.py` trains the models and stores their weights in `model_weights/`, `evaluate.py` evaluates the models on several metrics. 

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
```
cd 1a
docker build -t models .
docker run --name models .

```


