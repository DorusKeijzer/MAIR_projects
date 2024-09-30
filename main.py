import os
from assignment_1b.transition_manager import TransitionManager, State
from assignment_1a.read_data import train_data_bow, train_label
from assignment_1a.models import DecisionTreeModel
from assignment_1b.extract_preferences import PreferenceExtractor
from assignment_1b.lookup_restaurant import RestaurantLookup
import assignment_1c.config

# Initialize the dialogue system components
preference_extractor = PreferenceExtractor()
restaurant_lookup = RestaurantLookup()
tm = None  # Will be initialized later


def initialize_states():
    # Terminal state
    goodbye = State("11. Goodbye", terminal=True)

    # Suggest restaurant state
    suggest = State("5. Suggest restaurant")
    suggest.transitions = {
        "thankyou": ([], goodbye),
        "reqalts": ([], suggest)
    }
    suggest.make_suggestion = True

    # Additional requirements state
    ask_additional_requirements = State("12. Ask additional requirements",
                                        transitions={
                                            "inform": ([], suggest)
                                        })

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

    ask_price_range = State("3. Ask price range",
                            transitions={
                                "inform": (["location", "price_range"], ask_food_type)
                            },
                            optional=True)

    ask_area = State("2. Ask Area",
                     transitions={
                         "inform": (["location"], ask_price_range)
                     },
                     optional=True)

    # Confirmation state
    confirmation = State("Confirmation")
    # Transitions are handled in process_user_input

    # Initial state
    welcome = State("1. Welcome",
                    transitions={
                        "inform": ([], ask_area)
                    })

    # Set prompts based on language style
    if assignment_1c.config.use_formal_language:
        welcome.prompt = "Good day. How may I assist you in finding a suitable restaurant?"
        ask_area.prompt = "Could you please specify the area in which you would like to dine?"
        ask_price_range.prompt = "May I inquire about your preferred price range? (e.g., cheap, moderate, expensive)"
        ask_food_type.prompt = "What type of cuisine do you prefer?"
        ask_additional_requirements.prompt = "Do you have any additional requirements?"
        goodbye.prompt = "Thank you for using our service. Have a pleasant day!"
        suggest.prompt = "Based on your preferences, I recommend the following restaurant."
    else:
        welcome.prompt = "Hi there! What kind of restaurant are you looking for?"
        ask_area.prompt = "Which part of town do you wanna eat in?"
        ask_price_range.prompt = "What's your budget? (e.g., cheap, moderate, expensive)"
        ask_food_type.prompt = "What kind of food are you into?"
        ask_additional_requirements.prompt = "Anything else you're looking for?"
        goodbye.prompt = "Thanks for stopping by! Bye!"
        suggest.prompt = "Here's a restaurant you might like based on what you told me."

    # Confirmation prompt will be set dynamically
    confirmation.prompt = ""

    # Add the confirmation state to the list of states
    states = [
        ask_area,
        ask_price_range,
        ask_food_type,
        collect_candidates,
        ask_additional_requirements,
        suggest,
        goodbye,
        welcome,
        confirmation
    ]

    # Initialize TransitionManager
    tm = TransitionManager(states, welcome)

    return tm


def process_user_input(user_input, tm, preference_extractor, model, restaurant_lookup):
    # Handle confirmation responses
    if tm.current_state.name == "Confirmation":
        if user_input.lower() in ['yes', 'yeah', 'yup', 'correct', 'right']:
            # Confirm preference
            tm.update_preferences(tm.pending_pref_key, tm.pending_pref_value)
            tm.pending_pref_key = None
            tm.pending_pref_value = None

            # Determine the next state based on which preferences are still missing
            if tm.preferences['location'] is None:
                tm.set_state("2. Ask Area")
            elif tm.preferences['price_range'] is None:
                tm.set_state("3. Ask price range")
            elif tm.preferences['food_type'] is None:
                tm.set_state("4. Ask food type")
            else:
                tm.set_state("collect_candidates")
            tm.speak()
            # Do not return here; allow the function to continue
        else:
            # User did not confirm; re-ask the preference
            pref_key = tm.pending_pref_key
            tm.pending_pref_key = None
            tm.pending_pref_value = None

            # Set state back to the appropriate 'Ask' state
            if pref_key == 'food_type':
                tm.set_state("4. Ask food type")
            elif pref_key == 'price_range':
                tm.set_state("3. Ask price range")
            elif pref_key == 'location':
                tm.set_state("2. Ask Area")
            tm.speak()
            return  # Return here since we're re-asking the question

    else:
        # Extract preferences
        preferences, _ = preference_extractor.extract_preferences(user_input)
        preference_updated = False
        for pref_key, pref_value in preferences.items():
            if pref_value is not None:
                if tm.preferences.get(pref_key) is not None and not assignment_1c.config.allow_preference_change:
                    # Preference already set and changes not allowed
                    message = f"Sorry, you cannot change your {
                        pref_key.replace('_', ' ')} preference."
                    if assignment_1c.config.all_caps:
                        message = message.upper()
                    print(message)
                else:
                    if assignment_1c.config.ask_preference_confirmation:
                        # Save the current preference for confirmation
                        tm.pending_pref_key = pref_key
                        tm.pending_pref_value = pref_value
                        # Set to Confirmation state
                        tm.set_state("Confirmation")
                        tm.current_state.prompt = f"Did you mean {pref_key.replace('_', ' ')}: {
                            pref_value}? (yes/no)"
                        if assignment_1c.config.all_caps:
                            tm.current_state.prompt = tm.current_state.prompt.upper()
                        tm.speak()
                        return
                    else:
                        tm.update_preferences(pref_key, pref_value)
                        preference_updated = True

        # Predict dialogue act
        if preference_updated:
            dialogue_act = 'inform'
        else:
            dialogue_act = model.predict(user_input)

        # Transition state
        tm.transition(dialogue_act)
        tm.speak()

    # Handle candidate retrieval when in 'collect_candidates' state
    if tm.current_state.name == "collect_candidates":
        # Get candidate restaurants
        tm.candidate_restaurants = restaurant_lookup.get_candidates(
            tm.preferences)
        # Transition to 'ask_additional_requirements' without user input
        tm.set_state("12. Ask additional requirements")
        tm.speak()
        return  # Return here to prevent further code execution

    # If in the suggest state, make a suggestion
    if tm.current_state.make_suggestion:
        make_suggestion(tm, restaurant_lookup)


def make_suggestion(tm, restaurant_lookup):
    # Apply inference rules and select a restaurant
    selected_restaurant_data = restaurant_lookup.apply_inference_and_select(
        tm.candidate_restaurants, tm.additional_requirements)

    if isinstance(selected_restaurant_data, str):
        # Handle the case when no matching restaurants are found
        message = selected_restaurant_data
        if assignment_1c.config.all_caps:
            message = message.upper()
        print(message)
    else:
        selected_restaurant = selected_restaurant_data['restaurant']
        # Present the recommendation with reasoning
        reasoning = restaurant_lookup.generate_reasoning(
            selected_restaurant_data, tm.additional_requirements)
        output = (f"I recommend '{selected_restaurant['restaurantname']}', it is an "
                  f"{selected_restaurant['pricerange']} {
                      selected_restaurant['food']} restaurant "
                  f"in the {selected_restaurant['area']} of town.")
        if reasoning:
            output += "\n" + reasoning
        if assignment_1c.config.all_caps:
            output = output.upper()
        print(output)
        # Transition to goodbye state
        tm.set_state("11. Goodbye")
        tm.speak()


if __name__ == "__main__":
    # Initialize the TransitionManager and model
    tm = initialize_states()
    model = DecisionTreeModel(train_data_bow, train_label)
    weights_path = os.path.join(
        os.getcwd(), "assignment_1a", "model_weights", "decision_tree_model.joblib")
    model.load_weights(weights_path)
    # Start the dialogue
    tm.speak()
    while not tm.dead:
        user_input = input("Your answer: ")
        process_user_input(
            user_input, tm, preference_extractor, model, restaurant_lookup)
