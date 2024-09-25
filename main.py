
from assignment_1b.transition_manager import TransitionManager, State
from assignment_1a.read_data import train_data_bow, train_label
from assignment_1a.models import DecisionTreeModel  # , FeedForwardNNMode
from assignment_1b.extract_preferences import PreferenceExtractor
from assignment_1b.lookup_restaurant import RestaurantLookup
import os

# transition prediction model
model = DecisionTreeModel(train_data_bow, train_label)
weights_path = os.path.join(
    "assignment_1a", "model_weights", "decision_tree_model.joblib")
model.load_weights(weights_path)


##############################################

# states and transitions

##############################################

# Terminal state
goodbye = State("11. Goodbye", terminal=True)

# Suggest restaurant state
suggest = State("5. Suggest restaurant")

# allows for self referential relation
suggest.transitions = {
    "thankyou": ([], goodbye),
    "reqalts": ([], suggest)
}
suggest.make_suggestion = True

# Information giving states
give_area = State("10. Give restaurant area",
                  transitions={
                      "thankyou": ([], goodbye),
                      "reqalts": ([], suggest)
                  }
                  )

give_price_range = State("9. Give restaurant price range",
                         transitions={
                             "thankyou": ([], goodbye),
                             "reqalts": ([], suggest)
                         }
                         )

give_food_type = State("8. Give restaurant food type",
                       transitions={
                           "thankyou": ([], goodbye),
                           "reqalts": ([], suggest)
                       }
                       )

give_address = State("7. Give restaurant address",
                     transitions={
                         "thankyou": ([], goodbye),
                         "reqalts": ([], suggest)
                     }
                     )

give_phone_number = State("6. Give restaurant phone number",
                          transitions={
                              "thankyou": ([], goodbye),
                              "reqalts": ([], suggest)
                          }
                          )

# Information gathering states
ask_food_type = State("4. Ask food type",
                      transitions={
                          "inform": (["location", "price_range", "food_type"], suggest)
                      },
                      optional=True
                      )

ask_price_range = State("3. Ask price range",
                        transitions={
                            "inform": (["location", "price_range"], ask_food_type)
                        },
                        optional=True
                        )

ask_area = State("2. Ask Area",
                 transitions={
                     "inform": (["location"], ask_price_range)
                 },
                 optional=True
                 )

# Initial state
welcome = State("1. Welcome",
                transitions={
                    "inform": ([], ask_area)
                }
                )
welcome.prompt = "Welcome to our restaurant recommendation service! What kind of restaurant are you looking for?"
ask_area.prompt = "In which area of the city would you like to dine?"
ask_price_range.prompt = "What price range are you looking for? (e.g., cheap, moderate, expensive)"
ask_food_type.prompt = "What type of cuisine are you interested in?"
give_area.prompt = "The restaurant is located in {area}. Is there anything else you'd like to know?"
give_price_range.prompt = "The restaurant's price range is {price_range}. Would you like any other information?"
give_food_type.prompt = "The restaurant serves {food_type} cuisine. Is there anything else you'd like to know?"
give_address.prompt = "The restaurant's address is {address}. Do you need any other details?"
give_phone_number.prompt = "The restaurant's phone number is {phone_number}. Is there anything else I can help you with?"
suggest.prompt = "Based on your preferences, I recommend the following restaurant."
goodbye.prompt = "Thank you for using our service. Goodbye!"
# TransitionManager initialization
tm = TransitionManager([
    ask_area,
    ask_price_range,
    ask_food_type,
    give_area,
    give_address,
    give_food_type,
    give_price_range,
    give_phone_number,
    suggest,
    goodbye,
    welcome
], welcome)

preference_extractor = PreferenceExtractor()
restaurant_lookup = RestaurantLookup()

##############################################

# Dialogue loop

##############################################
if __name__ == "__main__":
    tm.speak()
    while not tm.dead:

        if tm.current_state.make_suggestion:
            restaurant = restaurant_lookup.lookup(tm.preferences)
            print(restaurant)
        user_input = input("Your answer: ")
        # print(f"User: {user_input}")

        # updates the preferences
        preferences, fallback = preference_extractor.extract_preferences(
            user_input)
        for pref_key in preferences.keys():
            if (pref_value := preferences[pref_key]) is not None:
                tm.update_preferences(pref_key, pref_value)
        # print(f"Preferences: {preferences}")

        # predicts intent
        dialogue_act = model.predict(user_input)
        # print(f"Predicted dialogue act: {dialogue_act}")

        # decides which way to transition based on preferences and intent
        success = tm.transition(dialogue_act)
        # print(f"Transition success: {success}")

        tm.speak()
