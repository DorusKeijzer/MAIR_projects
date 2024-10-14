import pyttsx3
import assignment_1c.config
from assignment_1b.transition_manager import TransitionManager, State
from assignment_1b.extract_preferences import PreferenceExtractor
from assignment_1a.models import DecisionTreeModel
from assignment_1b.lookup_restaurant import RestaurantLookup

class DialogueManager:
    def __init__(self, tm: TransitionManager, preference_extractor: PreferenceExtractor, model: DecisionTreeModel, restaurant_lookup: RestaurantLookup):
        self.tm = tm
        self.preference_extractor = preference_extractor
        self.model = model
        self.restaurant_lookup = restaurant_lookup
        self.conversation_started = False

    def start_conversation(self):
        """Start the conversation and return the initial message."""
        print("starting conversation")
        if not self.conversation_started:
            self.conversation_started = True
            initial_response = self.tm.speak()
            return {"response": initial_response}
        else:
            return {"response": "Conversation already started."}

    def continue_conversation(self, user_input):
        """Continue the conversation based on user input."""
        print("Continue the conversation based on user input.")
        if not self.conversation_started:
            return {"response": "Conversation not started. Please start the conversation first."}

        if self.tm.dead or self.tm.current_state.terminal:
            return {"response": "Conversation ended."}

        self.process_input(user_input)
        response = self.tm.speak()
        return {"response": response}


    def process_input(self, user_input: str):
        """Process user input and handle transitions between states."""
        # Predict the dialogue act using the ML model
        if user_input:
            dialogue_act = self.model.predict(user_input)
        else:
            dialogue_act = ""

        # Handle the current state based on the dialogue act and preferences
        state_name = self.tm.current_state.name
        
        if state_name == "1. Welcome":
            self.handle_post_welcome_transition(user_input)
        elif state_name == "Confirmation":
            self.handle_confirmation(user_input, dialogue_act)
        elif state_name == '2. Ask Area':
            self.handle_ask_area(user_input, dialogue_act)
        elif state_name == '3. Ask Price Range':
            self.handle_ask_price_range(user_input, dialogue_act)
        elif state_name == '4. Ask Food Type':
            self.handle_ask_food_type(user_input, dialogue_act)
        elif state_name == '5. Collect Candidates':
            self.handle_collect_candidates()
        elif state_name == '6. Ask Additional Requirements':
            self.handle_ask_additional_requirements(user_input, dialogue_act)
        elif state_name == '7. Suggest Restaurant':
            self.handle_suggest_restaurant()
        elif state_name == '8. Reply Additional Information':
            self.handle_reply_additional_information()
        elif state_name == '10. Intermediate (Alternative) State':
            self.handle_intermediate_state(user_input, dialogue_act)
        elif state_name == '9. Goodbye':
            self.handle_goodbye()

    def handle_welcome(self):
        """State 1: Welcome. Transition to post-welcome."""
        # Transition to Post-Welcome Transition
        self.tm.set_state("Post-Welcome Transition")
        self.tm.speak()

    def handle_post_welcome_transition(self, user_input: str):
        """Post-Welcome Transition: Analyze input and proceed to next state."""
        # Extract preferences from the initial input
        extracted_prefs, _ = self.preference_extractor.extract_preferences(user_input)
        self.tm.preferences.update(extracted_prefs)

        # Determine which preferences are missing
        missing_preferences = [key for key in ['location', 'price_range', 'food_type'] if self.tm.preferences.get(key) is None]

        if not missing_preferences:
            # All preferences are provided; proceed to collect candidates
            self.tm.set_state("5. Collect Candidates")
            self.tm.speak()
        else:
            # Determine the next state based on missing preferences
            next_state = self.determine_next_state(self.tm.preferences)
            if assignment_1c.config.ask_preference_confirmation:
                # Set to 'Confirmation' state to confirm the first missing preference
                pref_key = next_state.split('. ')[1].lower().replace(' ', '_')  # e.g., "2. Ask Area" -> "area"
                pref_value = self.tm.preferences.get(pref_key)
                if pref_value:
                    # If a value was already provided, prepare to confirm it
                    prompt = self.generate_confirmation_prompt(pref_key, pref_value)
                else:
                    # No value provided yet; proceed to ask the preference
                    prompt = self.generate_ask_preference_prompt(pref_key)
                self.tm.pending_pref_key = pref_key
                self.tm.pending_pref_value = pref_value
                self.tm.set_state("Confirmation", prompt=prompt)
                self.tm.speak()
            else:
                # Directly set to the first missing preference state
                self.tm.set_state(next_state)
                self.tm.speak()

    def handle_confirmation(self, user_input: str, dialogue_act: str):
        """State: Confirmation. Ask the user to confirm the extracted preference."""
        if dialogue_act in ['affirm', 'yes', 'confirm']:
            # User confirms the preference
            pref_key = self.tm.pending_pref_key
            pref_value = self.tm.pending_pref_value
            self.tm.update_preferences(pref_key, pref_value)

            # Determine the next state after confirmation
            next_state = self.determine_next_state(self.tm.preferences)
            self.tm.set_state(next_state)
            self.tm.speak()

        elif dialogue_act in ['deny', 'no', 'negate']:
            # User denies the preference, reset it
            pref_key = self.tm.pending_pref_key
            self.tm.update_preferences(pref_key, None)  # Reset the preference

            # Ask the question again
            next_state = self.determine_next_state(self.tm.preferences)
            self.tm.set_state(next_state)
            self.tm.speak()

        else:
            # Handle invalid inputs during confirmation
            self.handle_invalid_input("confirmation")

    def handle_ask_area(self, user_input: str, dialogue_act: str):
        """State 2: Ask user for area."""
        if dialogue_act == "inform":
            # Extract preferences from user input
            extracted_prefs, _ = self.preference_extractor.extract_preferences(user_input)

            # Check if location was extracted
            if extracted_prefs.get('location'):
                if assignment_1c.config.ask_preference_confirmation:
                    # Set to 'Confirmation' state before updating preferences
                    self.tm.pending_pref_key = 'location'
                    self.tm.pending_pref_value = extracted_prefs['location']
                    prompt = self.generate_confirmation_prompt('location', extracted_prefs['location'])
                    self.tm.set_state("Confirmation", prompt=prompt)
                else:
                    # Directly update preferences and move to the next state
                    self.tm.update_preferences('location', extracted_prefs['location'])
                    next_state = self.determine_next_state(self.tm.preferences)
                    self.tm.set_state(next_state)
                self.tm.speak()
            else:
                # Handle invalid input for the area
                self.handle_invalid_input("area")
        else:
            # Handle unexpected dialogue acts or invalid input
            self.handle_invalid_input("area")

    def handle_ask_price_range(self, user_input: str, dialogue_act: str):
        """State 3: Ask user for price range."""
        if dialogue_act == "inform":
            # Extract preferences from user input
            extracted_prefs, _ = self.preference_extractor.extract_preferences(user_input)

            # Check if price range was extracted
            if extracted_prefs.get('price_range'):
                if assignment_1c.config.ask_preference_confirmation:
                    # Set to 'Confirmation' state before updating preferences
                    self.tm.pending_pref_key = 'price_range'
                    self.tm.pending_pref_value = extracted_prefs['price_range']
                    prompt = self.generate_confirmation_prompt('price_range', extracted_prefs['price_range'])
                    self.tm.set_state("Confirmation", prompt=prompt)
                else:
                    # Directly update preferences and move to the next state
                    self.tm.update_preferences('price_range', extracted_prefs['price_range'])
                    next_state = self.determine_next_state(self.tm.preferences)
                    self.tm.set_state(next_state)
                self.tm.speak()
            else:
                # Handle invalid input for the price range
                self.handle_invalid_input("price range")
        else:
            # Handle unexpected dialogue acts or invalid input
            self.handle_invalid_input("price range")

    def handle_ask_food_type(self, user_input: str, dialogue_act: str):
        """State 4: Ask user for food type."""
        if dialogue_act == "inform":
            # Extract preferences from user input
            extracted_prefs, _ = self.preference_extractor.extract_preferences(user_input)

            # Check if food type was extracted
            if extracted_prefs.get('food_type'):
                if assignment_1c.config.ask_preference_confirmation:
                    # Set to 'Confirmation' state before updating preferences
                    self.tm.pending_pref_key = 'food_type'
                    self.tm.pending_pref_value = extracted_prefs['food_type']
                    prompt = self.generate_confirmation_prompt('food_type', extracted_prefs['food_type'])
                    self.tm.set_state("Confirmation", prompt=prompt)
                else:
                    # Directly update preferences and move to the next state
                    self.tm.update_preferences('food_type', extracted_prefs['food_type'])
                    next_state = self.determine_next_state(self.tm.preferences)
                    self.tm.set_state(next_state)
                self.tm.speak()
            else:
                # Handle invalid input for the food type
                self.handle_invalid_input("food type")
        else:
            # Handle unexpected dialogue acts or invalid input
            self.handle_invalid_input("food type")

    def determine_next_state(self, preferences):
        """Determine the next state based on missing preferences."""
        if preferences.get('location') is None:
            return "2. Ask Area"
        elif preferences.get('price_range') is None:
            return "3. Ask Price Range"
        elif preferences.get('food_type') is None:
            return "4. Ask Food Type"
        return "5. Collect Candidates"

    def handle_collect_candidates(self):
        """State 5: Collect restaurant candidates based on preferences."""
        self.tm.candidate_restaurants = self.restaurant_lookup.get_candidates(self.tm.preferences)
        self.tm.set_state("6. Ask Additional Requirements")
        self.tm.speak()

    def handle_ask_additional_requirements(self, user_input: str, dialogue_act: str):
        """State 6: Ask for additional requirements."""
        if dialogue_act in ["deny", "negate"]:
            # User indicates no additional requirements; suggest a restaurant directly
            self.suggest_restaurant(allow_alternatives=False)
            self.tm.set_state("7. Suggest Restaurant")
            self.tm.speak()
        elif dialogue_act in ["affirm", "request", "remove", "confirm", "ack"]:
            # Extract additional requirements
            additional_requirements, _ = self.preference_extractor.extract_additional_requirements(user_input)
            if isinstance(additional_requirements, dict) and additional_requirements:
                self.tm.additional_requirements.update(additional_requirements)
            # After updating requirements, suggest a restaurant
            self.suggest_restaurant(allow_alternatives=True)
        else:
            # Handle unexpected dialogue acts in Additional Requirements state
            self.handle_invalid_input("additional requirements")

    def suggest_restaurant(self, allow_alternatives=False):
        """Suggest a restaurant based on preferences and additional requirements."""
        candidates = self.restaurant_lookup.get_candidates(self.tm.preferences)
        selected_restaurant_data = self.restaurant_lookup.apply_inference_and_select(candidates, self.tm.additional_requirements)

        if isinstance(selected_restaurant_data, str):
            if allow_alternatives:
                no_match_message = "No matching restaurants found. Suggesting alternatives."
                if assignment_1c.config.all_caps:
                    no_match_message = no_match_message.upper()
                print(no_match_message)
                if assignment_1c.config.text_to_speech:
                    self.tm.tts_engine.say(no_match_message)
                    self.tm.tts_engine.runAndWait()

                selected_restaurant_data = self.restaurant_lookup.apply_inference_and_select(candidates, {})
                if isinstance(selected_restaurant_data, str):
                    no_alternatives_message = "No suitable alternatives found."
                    if assignment_1c.config.all_caps:
                        no_alternatives_message = no_alternatives_message.upper()
                    print(no_alternatives_message)
                    if assignment_1c.config.text_to_speech:
                        self.tm.tts_engine.say(no_alternatives_message)
                        self.tm.tts_engine.runAndWait()
                else:
                    # Provide reasoning and recommendation message
                    reasoning = self.restaurant_lookup.generate_reasoning(selected_restaurant_data, {})
                    recommendation_message = f"I recommend {selected_restaurant_data['restaurant']['restaurantname']}. {reasoning}"
                    if assignment_1c.config.use_formal_language:
                        recommendation_message = f"Based on your initial preferences, I recommend {selected_restaurant_data['restaurant']['restaurantname']}."
                    if assignment_1c.config.all_caps:
                        recommendation_message = recommendation_message.upper()
                    print(recommendation_message)
                    if assignment_1c.config.text_to_speech:
                        self.tm.tts_engine.say(recommendation_message)
                        self.tm.tts_engine.runAndWait()
            else:
                # No alternatives allowed, just conclude with the message
                message = "No matching restaurants found." if not assignment_1c.config.use_formal_language else "Regrettably, no restaurants meet your preferences."
                if assignment_1c.config.all_caps:
                    message = message.upper()
                print(message)
                if assignment_1c.config.text_to_speech:
                    self.tm.tts_engine.say(message)
                    self.tm.tts_engine.runAndWait()
        else:
            # A restaurant was found with the additional requirements, provide reasoning and recommendation
            reasoning = self.restaurant_lookup.generate_reasoning(selected_restaurant_data, self.tm.additional_requirements)
            message = f"I recommend {selected_restaurant_data['restaurant']['restaurantname']}. {reasoning}"
            if assignment_1c.config.use_formal_language:
                message = f"Based on your preferences, I recommend {selected_restaurant_data['restaurant']['restaurantname']}. {reasoning}"
            if assignment_1c.config.all_caps:
                message = message.upper()
            print(message)
            if assignment_1c.config.text_to_speech:
                self.tm.tts_engine.say(message)
            self.tm.tts_engine.runAndWait()

        self.tm.set_state("10. Intermediate (Alternative) State")
        self.tm.speak()


    def handle_suggest_restaurant(self):
        """State 7: Suggest a restaurant."""
    
        # Get restaurant candidates based on user preferences
        candidates = self.restaurant_lookup.get_candidates(self.tm.preferences)
    
        # Apply inference and select a restaurant based on additional requirements
        selected_restaurant_data = self.restaurant_lookup.apply_inference_and_select(candidates, self.tm.additional_requirements)
    
        if isinstance(selected_restaurant_data, str):
            # Handle case where no restaurant is found
            message = "No matching restaurants found." if not assignment_1c.config.use_formal_language else "Regrettably, no restaurants meet your preferences."
            if assignment_1c.config.all_caps:
                message = message.upper()
            print(message)
            if assignment_1c.config.text_to_speech:
                self.tm.tts_engine.say(message)
                self.tm.tts_engine.runAndWait()

        else:
            # Generate reasoning/explanation for why this restaurant was selected
            reasoning = self.restaurant_lookup.generate_reasoning(selected_restaurant_data, self.tm.additional_requirements)
        
            # Combine the recommendation and reasoning into a single message
            message = f"I recommend {selected_restaurant_data['restaurant']['restaurantname']}. {reasoning}"
        
            # Formal vs informal language
            if assignment_1c.config.use_formal_language:
                message = f"Based on your preferences, I recommend {selected_restaurant_data['restaurant']['restaurantname']}. {reasoning}"
        
            # Convert to uppercase if required
            if assignment_1c.config.all_caps:
                message = message.upper()
        
            # Print and optionally speak the message
            print(message)
            if assignment_1c.config.text_to_speech:
                self.tm.tts_engine.say(message)
                self.tm.tts_engine.runAndWait()

        # Set the next state
        self.tm.set_state("10. Intermediate (Alternative) State")
        self.tm.speak()



    def handle_reply_additional_information(self):
        """State 8: Provide additional information about the restaurant."""
        additional_info = self.restaurant_lookup.get_additional_info(self.tm.candidate_restaurants)
        if additional_info:
            output = additional_info.upper() if assignment_1c.config.all_caps else additional_info
            print(output)
            if assignment_1c.config.text_to_speech:
                self.tm.tts_engine.say(output)
                self.tm.tts_engine.runAndWait()
        else:
            message = "I have no further information at the moment." if not assignment_1c.config.use_formal_language else "I have no further information at the moment."
            if assignment_1c.config.all_caps:
                message = message.upper()
            print(message)
            if assignment_1c.config.text_to_speech:
                self.tm.tts_engine.say(message)
                self.tm.tts_engine.runAndWait()
        # Transition back to Intermediate State
        self.tm.set_state("10. Intermediate (Alternative) State")
        self.tm.speak()

    def handle_intermediate_state(self, user_input: str, dialogue_act: str):
        """State 10: Handle the intermediate state."""
        if dialogue_act in ['reqalts', 'request', 'reqmore', 'alternative', 'another option', 'another restaurant']:
            self.tm.set_state("7. Suggest Restaurant")
            self.tm.speak()
        elif dialogue_act in ['askinfo', 'information', 'more info', 'details']:
            self.tm.set_state("8. Reply Additional Information")
            self.tm.speak()
        elif dialogue_act in ['affirm', 'ack']:
            clarification = "Great! Is there anything else you're looking for?" if not assignment_1c.config.use_formal_language else "Is there anything else you need?"
            if assignment_1c.config.all_caps:
                clarification = clarification.upper()
            print(clarification)
            if assignment_1c.config.text_to_speech:
                self.tm.tts_engine.say(clarification)
                self.tm.tts_engine.runAndWait()
            self.tm.set_state("6. Ask Additional Requirements")
            self.tm.speak()
        elif dialogue_act in ['bye', 'thankyou', 'thank you', 'deny', 'negate']:
            goodbye_message = "Thank you for using our service. Have a pleasant day!" if assignment_1c.config.use_formal_language else "Alright, thank you for using our service. Have a great day!"
            if assignment_1c.config.all_caps:
                goodbye_message = goodbye_message.upper()
            print(goodbye_message)
            if assignment_1c.config.text_to_speech:
                self.tm.tts_engine.say(goodbye_message)
                self.tm.tts_engine.runAndWait()
            self.tm.set_state("9. Goodbye")
            self.tm.speak()
        else:
            self.handle_invalid_input("intermediate state")

    def handle_goodbye(self):
        """State 9: End the conversation."""
        self.tm.speak()
        self.tm.dead = True

    def handle_invalid_input(self, context: str):
        """Handle invalid user input based on the context."""
        clarification = f"I'm sorry, I didn't understand that. Could you please clarify your {context}?" if not assignment_1c.config.all_caps else f"I'M SORRY, I DIDN'T UNDERSTAND THAT. COULD YOU PLEASE CLARIFY YOUR {context.upper()}?"
        print(clarification)
        if assignment_1c.config.text_to_speech:
            self.tm.tts_engine.say(clarification)
            self.tm.tts_engine.runAndWait()

    def generate_confirmation_prompt(self, pref_key: str, pref_value: str) -> str:
        """Generate a confirmation prompt based on the preference key and value."""
        formal_prompts = {
            'location': f"You mentioned you would like to dine in {pref_value}. Is that correct?",
            'price_range': f"You indicated a price range of {pref_value}. Is that accurate?",
            'food_type': f"You prefer {pref_value} cuisine. Is that correct?"
        }
        informal_prompts = {
            'location': f"You wanna eat in {pref_value}? Is that right?",
            'price_range': f"Your budget is {pref_value}? Got it!",
            'food_type': f"You're into {pref_value} food? Cool!"
        }
        if assignment_1c.config.use_formal_language:
            prompt = formal_prompts.get(pref_key, "Is that correct?")
        else:
            prompt = informal_prompts.get(pref_key, "Is that right?")
        if assignment_1c.config.all_caps:
            prompt = prompt.upper()
        return prompt

    def generate_ask_preference_prompt(self, pref_key: str) -> str:
        """Generate a prompt to ask for a preference based on the preference key."""
        formal_prompts = {
            'location': "Could you please specify the area in which you would like to dine?",
            'price_range': "May I inquire about your preferred price range? (e.g., cheap, moderate, expensive)",
            'food_type': "What type of cuisine do you prefer?"
        }
        informal_prompts = {
            'location': "Which part of town do you wanna eat in?",
            'price_range': "What's your budget? (e.g., cheap, moderate, expensive)",
            'food_type': "What kind of food are you into?"
        }
        if assignment_1c.config.use_formal_language:
            prompt = formal_prompts.get(pref_key, "Could you please provide more details?")
        else:
            prompt = informal_prompts.get(pref_key, "Can you give me more info?")
        if assignment_1c.config.all_caps:
            prompt = prompt.upper()
        return prompt
