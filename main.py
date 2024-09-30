from assignment_1b.transition_manager import TransitionManager, State
from assignment_1a.read_data import train_data_bow, train_label
from assignment_1a.models import DecisionTreeModel
from assignment_1b.extract_preferences import PreferenceExtractor
from assignment_1b.lookup_restaurant import RestaurantLookup
import os

# Initialize the dialogue system components
preference_extractor = PreferenceExtractor()
restaurant_lookup = RestaurantLookup()
tm = None  # Will be initialized later

def initialize_states():
    # Terminal state
    goodbye = State("11. Goodbye", terminal=True)
    goodbye.prompt = "Thank you for using our service. Goodbye!"

    # Suggest restaurant state
    suggest = State("5. Suggest restaurant")
    suggest.transitions = {
        "thankyou": ([], goodbye),
        "reqalts": ([], suggest)
    }
    suggest.make_suggestion = True
    suggest.prompt = "Based on your preferences, I recommend the following restaurant."

    # Additional requirements state
    ask_additional_requirements = State("12. Ask additional requirements",
                                        transitions={
                                            "inform": ([], suggest)
                                        })
    ask_additional_requirements.prompt = "Do you have any additional requirements? (e.g., romantic, touristic)"

    # Collect candidates state
    collect_candidates = State("collect_candidates",
                               transitions={
                                   "": ([], ask_additional_requirements)
                               },
                               optional=False)

    # Information gathering states
    ask_food_type = State("4. Ask food type",
                          transitions={
                              "inform": (["location", "price_range", "food_type"], collect_candidates)
                          },
                          optional=True)
    ask_food_type.prompt = "What type of cuisine are you interested in?"

    ask_price_range = State("3. Ask price range",
                            transitions={
                                "inform": (["location", "price_range"], ask_food_type)
                            },
                            optional=True)
    ask_price_range.prompt = "What price range are you looking for? (e.g., cheap, moderate, expensive)"

    ask_area = State("2. Ask Area",
                     transitions={
                         "inform": (["location"], ask_price_range)
                     },
                     optional=True)
    ask_area.prompt = "In which area of the city would you like to dine?"

    # Initial state
    welcome = State("1. Welcome",
                    transitions={
                        "inform": ([], ask_area)
                    })
    welcome.prompt = "Welcome to our restaurant recommendation service! What kind of restaurant are you looking for?"

    # TransitionManager initialization
    states = [
        ask_area,
        ask_price_range,
        ask_food_type,
        collect_candidates,
        ask_additional_requirements,
        suggest,
        goodbye,
        welcome
    ]
    return TransitionManager(states, welcome)

def process_user_input(user_input, tm, preference_extractor, model, restaurant_lookup):
    # Extract preferences or additional requirements
    if tm.current_state.name == "12. Ask additional requirements":
        # Extract additional requirements
        additional_requirements = preference_extractor.extract_additional_requirements(user_input)
        tm.additional_requirements = additional_requirements
        dialogue_act = 'inform'  # Set dialogue act to 'inform' after extracting additional requirements
    else:
        # Extract preferences
        preferences, _ = preference_extractor.extract_preferences(user_input)
        preference_updated = False
        for pref_key, pref_value in preferences.items():
            if pref_value is not None and tm.preferences.get(pref_key) != pref_value:
                tm.update_preferences(pref_key, pref_value)
                preference_updated = True

        # Predict dialogue act
        dialogue_act = model.predict(user_input)

        # If preference was updated, set dialogue_act to 'inform' regardless
        if preference_updated:
            dialogue_act = 'inform'

    # Transition state
    tm.transition(dialogue_act)

    # Handle candidate retrieval when in 'collect_candidates' state
    if tm.current_state.name == "collect_candidates":
        # Get candidate restaurants
        tm.candidate_restaurants = restaurant_lookup.get_candidates(tm.preferences)
        # Transition to 'ask_additional_requirements' without user input
        tm.set_state("12. Ask additional requirements")
        tm.speak()
    else:
        tm.speak()

    # If in the suggest state, make a suggestion
    if tm.current_state.make_suggestion:
        make_suggestion(tm, restaurant_lookup)

def make_suggestion(tm, restaurant_lookup):
    # Apply inference rules and select a restaurant
    selected_restaurant_data = restaurant_lookup.apply_inference_and_select(
        tm.candidate_restaurants, tm.additional_requirements)

    if isinstance(selected_restaurant_data, str):
        # Handle the case when no matching restaurants are found
        print(selected_restaurant_data)
    else:
        selected_restaurant = selected_restaurant_data['restaurant']
        # Present the recommendation with reasoning
        reasoning = restaurant_lookup.generate_reasoning(
            selected_restaurant_data, tm.additional_requirements)
        print(f"I recommend '{selected_restaurant['restaurantname']}', it is an {selected_restaurant['pricerange']} {selected_restaurant['food']} restaurant in the {selected_restaurant['area']} of town.")
        if reasoning:
            print(reasoning)
        # Transition to goodbye state
        tm.set_state("11. Goodbye")
        tm.speak()

if __name__ == "__main__":
    # Initialize the TransitionManager and model
    tm = initialize_states()
    model = DecisionTreeModel(train_data_bow, train_label)
    weights_path = os.path.join(
        "MAIR_projects", "assignment_1a", "model_weights", "decision_tree_model.joblib")
    model.load_weights(weights_path)
    # Start the dialogue
    tm.speak()
    while not tm.dead:
        user_input = input("Your answer: ")
        process_user_input(user_input, tm, preference_extractor, model, restaurant_lookup)