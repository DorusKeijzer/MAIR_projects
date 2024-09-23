from assignment_1b.transition_manager import TransitionManager, State
from assignment_1a.read_data import train_data_bow, train_label
from assignment_1a.models import DecisionTreeModel  # , FeedForwardNNMode

from assignment_1b.extract_preferences import PreferenceExtractor
import os

# neural network
# model = FeedForwardNNModel(train_data_bow, train_label)
# weights_path = os.path.join(
#    "assignment_1a", "model_weights", "feed_forward_nn_model.weights.h5")
# model.load_weights(weights_path)


model = DecisionTreeModel(train_data_bow, train_label)

weights_path = os.path.join(
    "assignment_1a", "model_weights", "decision_tree_model.joblib")
model.load_weights(weights_path)

##############################################

# Defining states and transitions

##############################################

goodbye = State("11. Goodbye", terminal=True)

suggest = State("5. Suggest restaurant")
suggest.transitions = {
    "thankyou": ([], goodbye),
    "reqalts": ([], suggest)
}

give_area = State("10. Give restaurant area.", transitions={
                  "thankyou": goodbye, "reqalts": ([], suggest)})
give_price_range = State("9. Give restaurant price range.", transitions={
    "thankyou": goodbye, "reqalts": ([], suggest)})
give_food_type = State("8. Give restaurant area.", transitions={
    "thankyou": goodbye, "reqalts": ([], suggest)})
give_address = State("7. Give restaurant address.", transitions={
    "thankyou": goodbye, "reqalts": ([], suggest)})
give_phone_number = State("6. Give restaurant area.", transitions={
    "thankyou": goodbye, "reqalts": ([], suggest)})
ask_food_type = State("4. Ask food type", {
                      "inform": (["location", "price_range", "food_type"], suggest)})

ask_price_range = State("3. Ask price range", {
                        "inform": (["location", "price_range"], suggest)})
ask_area = State("2. Ask Area", transitions={
                 "inform": (["location"], ask_price_range)})
welcome = State("1. Welcome, please tell me where you'd like to eat",
                transitions={"inform": ([], ask_area)})

tm = TransitionManager([ask_area, ask_price_range, ask_food_type, give_area, give_address,
                       give_food_type, give_price_range, give_phone_number, suggest, goodbye, welcome], welcome)
preference_extractor = PreferenceExtractor()


##############################################

# Dialogue loop

##############################################

print(f"Agent: {tm}")
while not tm.dead:
    user_input = input("Your answer: ")

    # updates the preferences
    preferences, fallback = preference_extractor.extract_preferences(
        user_input)
    for pref_key in preferences.keys():
        if (pref_value := preferences[pref_key]) is not None:
            tm.update_preferences(pref_key, pref_value)
    print(preferences)
    # predicis intent
    dialogue_act = model.predict(user_input)
    # decides which way to transition based on preferences and intent
    success = tm.transition(dialogue_act)
    print(success)
    print(f"Agent: {tm}")
