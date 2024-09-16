from models import DecisionTreeModel, LogisticRegressionModel, FeedForwardNNModel


for model in [DecisionTreeModel, LogisticRegressionModel, FeedForwardNNModel]:
    print(f'Training {model.name}...')
    model.fit()
    model.save_weights()
