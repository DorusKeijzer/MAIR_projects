from models import DecisionTreeModel, LogisticRegressionModel, FeedForwardNNModel
from read_data import train_label, train_data_bow

for model_class in [DecisionTreeModel, LogisticRegressionModel, FeedForwardNNModel]:
    model = model_class(train_data_bow, train_label)
    print(f'Training {model.name}...')
    model.train()
    model.save_weights()
