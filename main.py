import os
from assignment_1a.models import FeedForwardNNModel
from assignment_1a.read_data import train_data_bow, train_label
from assignment_1b.transition_manager import TransitionManager


model = FeedForwardNNModel(train_data_bow, train_label)

weights_path = os.path.join(
    "assignment_1a", "model_weights", "feed_forward_nn_model.weights.h5")
model.load_weights(weights_path)
