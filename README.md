for assignment 1a, see the readme inside of `1a/`

For the main program install dependencies and run main.py:

```bash
pip install -r requirements.txt
python main.py
```

To ensure you can run the program on your machine, there is also a Dockerfile that you can run if you known how to.

below we explain what each folder contains

## 1a 

here, several models are trained. their weights are stored in a designated directory. these weight can then be used in the main program and in the evaluation script 

## 1b

Contains the transition manager, a way to lookup restaurants and a way to extract preferences.

## 1c

The agent can be configured to exert different behavior by changing `configuration.py`

`/assignment_c/` further contains the inference engine and a script that randomly adds properties to our training data 
