import os
from assignment_1b.transition_manager import TransitionManager, State
from assignment_1a.read_data import train_data_bow, train_label
from assignment_1a.models import DecisionTreeModel
from assignment_1b.extract_preferences import PreferenceExtractor
from assignment_1b.lookup_restaurant import RestaurantLookup
from assignment_1c.reasoner import inference_engine, rule, literal
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

