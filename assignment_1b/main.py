from ..assignment_1a.models import FeedForwardNNModel

model = FeedForwardNNModel()

model.load_weights(
    "../assignment_1a/model_weights/feed_forward_nn_model.weights.h5")
