from assignment_1b.transition_manager import TransitionManager, State
from assignment_1a.read_data import train_data_bow, train_label
from assignment_1a.models import FeedForwardNNModel
import os


weights_path = os.path.join(
    "assignment_1a", "model_weights", "feed_forward_nn_model.weights.h5")
model.load_weights(weights_path)


# example on how to use

# transition table from the example in the assignment description

suggest = State("Suggest restaurant")
ask_area = State("Ask Area", transitions={"reply_area": suggest})
welcome = State("Welcome", transitions={
    "other": ask_area, "express_area": suggest})

tm = TransitionManager([suggest, ask_area, welcome], welcome)
print(f"Agent: {tm}")
while True:
    user_input = input("Your answer: ")
    dialogue_act = model.predict(user_input)
    tm.transition(dialogue_act)
    print(f"Agent: {tm}")
