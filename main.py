import os
from assignment_1b.transition_manager import TransitionManager, State
from assignment_1a.read_data import train_data_bow, train_label
from assignment_1a.models import DecisionTreeModel
from assignment_1b.extract_preferences import PreferenceExtractor
from assignment_1b.lookup_restaurant import RestaurantLookup
from assignment_1b.Dialogue_manager import DialogueManager
import assignment_1c.config

def initialize_states():
    """Initializes all dialogue states and returns a TransitionManager."""
    # Define all states
    welcome = State("1. Welcome")
    welcome.prompt = "Hi there! What kind of restaurant are you looking for?" if not assignment_1c.config.use_formal_language else "Good day. How may I assist you in finding a suitable restaurant?"

    confirmation = State("Confirmation")
    # Confirmation prompts are handled dynamically in DialogueManager

    post_welcome = State("Post-Welcome Transition")
    # No prompt needed; handled in DialogueManager

    ask_area = State("2. Ask Area")
    ask_area.prompt = "Which part of town do you wanna eat in?" if not assignment_1c.config.use_formal_language else "Could you please specify the area in which you would like to dine?"

    ask_price_range = State("3. Ask Price Range")
    ask_price_range.prompt = "What's your budget? (e.g., cheap, moderate, expensive)" if not assignment_1c.config.use_formal_language else "May I inquire about your preferred price range? (e.g., cheap, moderate, expensive)"

    ask_food_type = State("4. Ask Food Type")
    ask_food_type.prompt = "What kind of food are you into?" if not assignment_1c.config.use_formal_language else "What type of cuisine do you prefer?"

    collect_candidates = State("5. Collect Candidates")
    # No prompt needed; handled in DialogueManager

    ask_additional_requirements = State("6. Ask Additional Requirements")
    ask_additional_requirements.prompt = "Anything else you're looking for?" if not assignment_1c.config.use_formal_language else "Do you have any additional requirements?"

    suggest_restaurant = State("7. Suggest Restaurant")
    suggest_restaurant.prompt = "Here's a restaurant you might like based on what you told me." if not assignment_1c.config.use_formal_language else "Based on your preferences, I recommend the following restaurant."

    reply_additional_info = State("8. Reply Additional Information")
    reply_additional_info.prompt = "Here is more information about the restaurant." if not assignment_1c.config.use_formal_language else "Here are additional details about the restaurant."

    intermediate_state = State("10. Intermediate (Alternative) State")
    intermediate_state.prompt = "Can I help you in any other way?" if assignment_1c.config.use_formal_language else "Can I help you in any other way?"

    goodbye = State("9. Goodbye", terminal=True)
    goodbye.prompt = "Thanks for stopping by! Bye!" if not assignment_1c.config.use_formal_language else "Thank you for using our service. Have a pleasant day!"

    # Define transitions for each state
    # Welcome State
    welcome.transitions = {
        "inform": ([], "Post-Welcome Transition")
    }

    # Post-Welcome Transition State
    post_welcome.transitions = {
        "": ([], "Determine Next State")
    }

    # Ask Area State
    ask_area.transitions = {
        "inform": (["location"], "Confirmation")
    }

    # Ask Price Range State
    ask_price_range.transitions = {
        "inform": (["price_range"], "Confirmation")
    }

    # Ask Food Type State
    ask_food_type.transitions = {
        "inform": (["food_type"], "Confirmation")
    }

    # Collect Candidates State
    collect_candidates.transitions = {
        "": ([], "6. Ask Additional Requirements")
    }

    # Ask Additional Requirements State
    ask_additional_requirements.transitions = {
        "inform": ([], "7. Suggest Restaurant"),
        "deny": ([], "7. Suggest Restaurant")
    }

    # Suggest Restaurant State
    suggest_restaurant.transitions = {
        "thankyou": ([], "9. Goodbye"),
        "reqalts": ([], "7. Suggest Restaurant"),
        "askinfo": ([], "8. Reply Additional Information")
    }

    # Reply Additional Information State
    reply_additional_info.transitions = {
        "done": ([], "10. Intermediate (Alternative) State")
    }

    # Intermediate State
    intermediate_state.transitions = {
        "thankyou": ([], "9. Goodbye"),
        "reqalts": ([], "7. Suggest Restaurant"),
        "askinfo": ([], "8. Reply Additional Information"),
        "affirm": ([], "6. Ask Additional Requirements"),
        "deny": ([], "6. Ask Additional Requirements")
    }

    # Create a list of all states
    states = [
        welcome,
        confirmation,
        post_welcome,
        ask_area,
        ask_price_range,
        ask_food_type,
        collect_candidates,
        ask_additional_requirements,
        suggest_restaurant,
        reply_additional_info,
        intermediate_state,
        goodbye
    ]

    # Initialize TransitionManager with all states and starting with welcome
    tm = TransitionManager(states, welcome)
    return tm

if __name__ == "__main__":
    # Initialize the TransitionManager and model
    tm = initialize_states()
    preference_extractor = PreferenceExtractor()
    restaurant_lookup = RestaurantLookup()
    model = DecisionTreeModel(train_data_bow, train_label)
    
    # Load the model weights
    weights_path = os.path.join(os.getcwd(), "assignment_1a", "model_weights", "decision_tree_model_normal.joblib")
    model.load_weights(weights_path)
    
    # Initialize the DialogueManager and start the conversation
    dialogue_manager = DialogueManager(tm, preference_extractor, model, restaurant_lookup)
    dialogue_manager.start_conversation()
