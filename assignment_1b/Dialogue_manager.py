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
        self.messages = []

        self.suggested_restaurants = set()
        self.first_suggestion = True
        self.pending_messages = []  # Add this new attribute
    
    def start_conversation(self):
        """Start the conversation and return the initial message."""
        print("starting conversation")
        if not self.conversation_started:
            self.conversation_started = True
            initial_response = self.tm.speak()
            self.output_message(initial_response)
            return {"response": [initial_response]}
        else:
            return {"response": "Conversation already started."}



    def continue_conversation(self, user_input):
        """Continue the conversation based on user input."""
        if not self.conversation_started:
            return {"responses": ["Conversation not started. Please start the conversation first."]}

        if self.tm.dead or self.tm.current_state.terminal:
            return {"responses": ["Conversation ended."]}

        # Clear pending messages from previous turns
        self.pending_messages = []
        
        # Process input and collect messages
        self.process_input(user_input)


        # Handle automatic state transitions for collection and suggestion states
        if self.tm.current_state.name == "5. Collect Candidates":
            self.handle_collect_candidates()
        elif self.tm.current_state.name == "6. Ask Additional Requirements":
            response = self.tm.speak()
            if response is not None:
                self.output_message(response)

        # Get response from transition manager if no messages were collected
        if not self.pending_messages:
            response = self.tm.speak()
            if response is not None:
                self.output_message(response)

        # If still no messages were collected, something went wrong
        if not self.pending_messages:
            self.handle_error_state()
        
        return {"responses": "\n".join([msg for msg in self.pending_messages if msg is not None])}

    def process_input(self, user_input: str):
        if user_input:
            dialogue_act = self.model.predict(user_input)
        else:
            dialogue_act = ""

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
        elif state_name == '10. Intermediate (Alternative) State':
            self.handle_intermediate_state(user_input, dialogue_act)
        elif state_name == '9. Goodbye':
            self.handle_goodbye()

    def handle_post_welcome_transition(self, user_input: str):
        print(f"DEBUG: Handling post-welcome transition. User input: {user_input}")
        extracted_prefs, _ = self.preference_extractor.extract_preferences(user_input)
        print(f"DEBUG: Extracted preferences: {extracted_prefs}")

        if assignment_1c.config.ask_preference_confirmation:
            self.preferences_to_confirm = list(extracted_prefs.keys())
            self.extracted_prefs = extracted_prefs
            self.confirm_next_preference()
        else:
            self.tm.preferences.update(extracted_prefs)
            self.move_to_next_state()

        print(f"DEBUG: Current preferences after post-welcome: {self.tm.preferences}")

    def confirm_next_preference(self):
        print(f"DEBUG: Entering confirm_next_preference. Preferences to confirm: {self.preferences_to_confirm}")
        while self.preferences_to_confirm:
            pref_key = self.preferences_to_confirm.pop(0)
            pref_value = self.extracted_prefs[pref_key]
            print(f"DEBUG: Confirming preference: {pref_key} = {pref_value}")
            if pref_value is not None:
                prompt = self.generate_confirmation_prompt(pref_key, pref_value)
                self.tm.pending_pref_key = pref_key
                self.tm.pending_pref_value = pref_value
                self.tm.set_state("Confirmation", prompt=prompt)
                self.tm.speak()
                return
        
        print("DEBUG: All preferences confirmed. Moving to next state.")
        print(f"DEBUG: Final TransitionManager preferences: {self.tm.preferences}")
        self.move_to_next_state()

    def move_to_next_state(self):
        print("DEBUG: Moving to next state")
        missing_preferences = [key for key in ['location', 'price_range', 'food_type'] if self.tm.preferences.get(key) is None]
        print(f"DEBUG: Missing preferences: {missing_preferences}")

        if not missing_preferences:
            print("DEBUG: All preferences collected. Moving to Collect Candidates.")
            self.tm.set_state("5. Collect Candidates")
        else:
            next_state = self.determine_next_state(self.tm.preferences)
            print(f"DEBUG: Moving to state: {next_state}")
            if next_state == self.tm.current_state.name:
                print("DEBUG: Warning: Attempting to move to the same state. Moving to Collect Candidates instead.")
                self.tm.set_state("5. Collect Candidates")
            else:
                self.tm.set_state(next_state)
        self.tm.speak()

    def handle_confirmation(self, user_input: str, dialogue_act: str):
        print(f"DEBUG: Handling confirmation. Dialogue act: {dialogue_act}")
        if dialogue_act in ['affirm', 'yes', 'confirm']:
            if hasattr(self.tm, 'pending_additional_req_key'):
                # Handling additional requirement confirmation
                req_key = self.tm.pending_additional_req_key
                req_value = self.tm.pending_additional_req_value
                print(f"DEBUG: Confirming additional requirement: {req_key} = {req_value}")
                self.tm.additional_requirements[req_key] = req_value
                print(f"DEBUG: Updated TransitionManager additional requirements: {self.tm.additional_requirements}")
                delattr(self.tm, 'pending_additional_req_key')
                delattr(self.tm, 'pending_additional_req_value')
                self.confirm_next_additional_requirement()
            else:
                # Handling primary preference confirmation
                pref_key = self.tm.pending_pref_key
                pref_value = self.tm.pending_pref_value
                print(f"DEBUG: Confirming preference: {pref_key} = {pref_value}")
                self.tm.preferences[pref_key] = pref_value
                if pref_key in self.extracted_prefs:
                    del self.extracted_prefs[pref_key]
                print(f"DEBUG: Updated TransitionManager preferences: {self.tm.preferences}")
                self.confirm_next_preference()
        elif dialogue_act in ['deny', 'no', 'negate']:
            if hasattr(self.tm, 'pending_additional_req_key'):
                # Handling additional requirement denial
                req_key = self.tm.pending_additional_req_key
                print(f"DEBUG: Denying additional requirement: {req_key}")
                delattr(self.tm, 'pending_additional_req_key')
                delattr(self.tm, 'pending_additional_req_value')
                self.confirm_next_additional_requirement()
            else:
                # Handling primary preference denial
                pref_key = self.tm.pending_pref_key
                print(f"DEBUG: Denying preference: {pref_key}")
                self.tm.preferences[pref_key] = None
                if pref_key in self.extracted_prefs:
                    del self.extracted_prefs[pref_key]
                print(f"DEBUG: Updated TransitionManager preferences: {self.tm.preferences}")
                self.move_to_next_state()
        else:
            self.handle_invalid_input("confirmation")

    def handle_ask_area(self, user_input: str, dialogue_act: str):
        if dialogue_act == "inform":
            extracted_prefs, _ = self.preference_extractor.extract_preferences(user_input)
            if extracted_prefs.get('location'):
                if assignment_1c.config.ask_preference_confirmation:
                    self.tm.pending_pref_key = 'location'
                    self.tm.pending_pref_value = extracted_prefs['location']
                    prompt = self.generate_confirmation_prompt('location', extracted_prefs['location'])
                    self.tm.set_state("Confirmation", prompt=prompt)
                else:
                    self.tm.update_preferences('location', extracted_prefs['location'])
                    next_state = self.determine_next_state(self.tm.preferences)
                    self.tm.set_state(next_state)
                self.tm.speak()
            else:
                self.handle_invalid_input("area")
        else:
            self.handle_invalid_input("area")

    def handle_ask_price_range(self, user_input: str, dialogue_act: str):
        if dialogue_act == "inform":
            extracted_prefs, _ = self.preference_extractor.extract_preferences(user_input)
            if extracted_prefs.get('price_range'):
                if assignment_1c.config.ask_preference_confirmation:
                    self.tm.pending_pref_key = 'price_range'
                    self.tm.pending_pref_value = extracted_prefs['price_range']
                    prompt = self.generate_confirmation_prompt('price_range', extracted_prefs['price_range'])
                    self.tm.set_state("Confirmation", prompt=prompt)
                else:
                    self.tm.update_preferences('price_range', extracted_prefs['price_range'])
                    next_state = self.determine_next_state(self.tm.preferences)
                    self.tm.set_state(next_state)
                self.tm.speak()
            else:
                self.handle_invalid_input("price range")
        else:
            self.handle_invalid_input("price range")

    def handle_ask_food_type(self, user_input: str, dialogue_act: str):
        if dialogue_act == "inform":
            extracted_prefs, _ = self.preference_extractor.extract_preferences(user_input)
            if extracted_prefs.get('food_type'):
                if assignment_1c.config.ask_preference_confirmation:
                    self.tm.pending_pref_key = 'food_type'
                    self.tm.pending_pref_value = extracted_prefs['food_type']
                    prompt = self.generate_confirmation_prompt('food_type', extracted_prefs['food_type'])
                    self.tm.set_state("Confirmation", prompt=prompt)
                else:
                    self.tm.update_preferences('food_type', extracted_prefs['food_type'])
                    next_state = self.determine_next_state(self.tm.preferences)
                    self.tm.set_state(next_state)
                self.tm.speak()
            else:
                self.handle_invalid_input("food type")
        else:
            self.handle_invalid_input("food type")

    def determine_next_state(self, preferences):
        if preferences.get('location') is None:
            return "2. Ask Area"
        elif preferences.get('price_range') is None:
            return "3. Ask Price Range"
        elif preferences.get('food_type') is None:
            return "4. Ask Food Type"
        return "5. Collect Candidates"  # Add this line to ensure we move to collect candidates when all preferences are filled


    def handle_collect_candidates(self):
        """Modified to properly chain through to restaurant suggestions"""
        print("DEBUG: Entering handle_collect_candidates")
        self.tm.candidate_restaurants = self.restaurant_lookup.get_candidates(self.tm.preferences)
        
        if self.tm.candidate_restaurants.empty:
            self.output_message("I apologize, but I couldn't find any restaurants matching your criteria.")
            self.handle_goodbye()
            return

        # Move directly to suggesting a restaurant if we have candidates
        print("DEBUG: Found candidates, moving to suggestion")
        self.suggest_restaurant(allow_alternatives=True)

    def handle_ask_additional_requirements(self, user_input: str, dialogue_act: str):
        if dialogue_act in ["deny", "negate"]:
            self.suggest_restaurant(allow_alternatives=False)
            self.tm.set_state("7. Suggest Restaurant")
            self.tm.speak()
        elif dialogue_act in ["affirm", "request", "remove", "confirm", "ack"]:
            additional_requirements, _ = self.preference_extractor.extract_additional_requirements(user_input)
            if isinstance(additional_requirements, dict) and additional_requirements:
                self.additional_requirements_to_confirm = list(additional_requirements.keys())
                self.extracted_additional_reqs = additional_requirements
                self.confirm_next_additional_requirement()
            else:
                self.suggest_restaurant(allow_alternatives=True)
        else:
            self.handle_invalid_input("additional requirements")

    def confirm_additional_requirements(self, additional_requirements):
        self.additional_requirements_to_confirm = list(additional_requirements.keys())
        self.extracted_additional_reqs = additional_requirements
        self.confirm_next_additional_requirement()

    def confirm_next_additional_requirement(self):
        if self.additional_requirements_to_confirm:
            req_key = self.additional_requirements_to_confirm.pop(0)
            req_value = self.extracted_additional_reqs[req_key]
            prompt = self.generate_additional_req_confirmation_prompt(req_key, req_value)
            self.tm.pending_additional_req_key = req_key
            self.tm.pending_additional_req_value = req_value
            self.tm.set_state("Confirmation", prompt=prompt)
            self.tm.speak()
        else:
            print("DEBUG: All additional requirements confirmed. Moving to suggest restaurant.")
            self.suggest_restaurant(allow_alternatives=True)

    def generate_additional_req_confirmation_prompt(self, req_key: str, req_value: bool) -> str:
        if assignment_1c.config.use_formal_language:
            return f"You mentioned you would like a {req_key} restaurant. Is that correct?"
        else:
            return f"So, you want a {req_key} place, right?"

    def suggest_restaurant(self, allow_alternatives=False):
        print("DEBUG: Entering suggest_restaurant method")
        print(f"DEBUG: Current preferences: {self.tm.preferences}")
        
        candidates = self.restaurant_lookup.get_candidates(self.tm.preferences)
        if candidates.empty:
            self.output_message("I apologize, but I couldn't find any restaurants matching your criteria.")
            self.handle_goodbye()
            return

        selected_restaurant_data = self.restaurant_lookup.apply_inference_and_select(candidates, {})
        if isinstance(selected_restaurant_data, dict):
            self.suggest_specific_restaurant(selected_restaurant_data, {}, is_alternative=False)
            # Move to intermediate state after suggestion
            self.tm.set_state("10. Intermediate (Alternative) State")
        else:
            self.output_message("I apologize, but I couldn't find a suitable restaurant.")
            self.handle_goodbye()            

    def suggest_specific_restaurant(self, selected_restaurant_data, requirements, is_alternative=False):
        restaurant_name = selected_restaurant_data['restaurant']['restaurantname']
        if restaurant_name not in self.suggested_restaurants:
            self.suggested_restaurants.add(restaurant_name)
            reasoning = self.restaurant_lookup.generate_reasoning(selected_restaurant_data, requirements)
            
            if is_alternative:
                if assignment_1c.config.use_formal_language:
                    message = f"I couldn't find an exact match, but I found an alternative that might interest you: {restaurant_name}. {reasoning}"
                else:
                    message = f"I couldn't find exactly what you wanted, but here's an option that might work: {restaurant_name}. {reasoning}"
            else:
                if assignment_1c.config.use_formal_language:
                    message = f"Based on your preferences, I recommend {restaurant_name}. {reasoning}"
                else:
                    message = f"How about {restaurant_name}? {reasoning}"
            
            self.output_message(message)
            self.ask_for_alternative()

    def handle_error_state(self):
        """Handle cases where no messages were generated"""
        if assignment_1c.config.use_formal_language:
            self.output_message("I apologize, but I encountered an issue processing your request. Would you like to try again?")
        else:
            self.output_message("Sorry, something went wrong. Want to try again?")

    def ask_for_alternative(self):
        if assignment_1c.config.use_formal_language:
            question = "Would you like to hear about another restaurant option?"
        else:
            question = "Want to hear about another restaurant?"
        self.output_message(question)

    def handle_suggest_restaurant(self):
        candidates = self.restaurant_lookup.get_candidates(self.tm.preferences)
        selected_restaurant_data = self.restaurant_lookup.apply_inference_and_select(candidates, self.tm.additional_requirements)
    
        if isinstance(selected_restaurant_data, str):
            message = "No matching restaurants found." if not assignment_1c.config.use_formal_language else "Regrettably, no restaurants meet your preferences."
            self.output_message(message)
        else:
            reasoning = self.restaurant_lookup.generate_reasoning(selected_restaurant_data, self.tm.additional_requirements)
            message = f"I recommend {selected_restaurant_data['restaurant']['restaurantname']}. {reasoning}"
            if assignment_1c.config.use_formal_language:
                message = f"Based on your preferences, I recommend {selected_restaurant_data['restaurant']['restaurantname']}. {reasoning}"
            self.output_message(message)

        self.tm.set_state("10. Intermediate (Alternative) State")
        self.tm.speak()

    def handle_intermediate_state(self, user_input: str, dialogue_act: str):
        print(f"DEBUG: Handling intermediate state. User input: {user_input}, Dialogue act: {dialogue_act}")
        
        if dialogue_act in ['affirm', 'yes', 'alternative', 'another option']:
            print("DEBUG: User requested alternative restaurant")
            self.suggest_alternative_restaurant()
        elif dialogue_act in ['deny', 'no', 'negate', 'bye', 'thankyou', 'thank you']:
            print("DEBUG: User declined alternative restaurant")
            self.handle_goodbye()
        else:
            print(f"DEBUG: Unrecognized dialogue act in intermediate state: {dialogue_act}")
            clarification = "I'm sorry, I didn't understand. Would you like to hear about another restaurant, or shall we end the conversation?" if assignment_1c.config.use_formal_language else "Sorry, I didn't catch that. Do you want to hear about another restaurant or are we done?"
            self.output_message(clarification)


    def suggest_alternative_restaurant(self):
        print(f"DEBUG: Entering suggest_alternative_restaurant")
        print(f"DEBUG: Current preferences: {self.tm.preferences}")
        print(f"DEBUG: Additional requirements: {self.tm.additional_requirements}")
        print(f"DEBUG: Previously suggested restaurants: {self.suggested_restaurants}")

        primary_preferences = {k: v for k, v in self.tm.preferences.items() if k in ['location', 'price_range', 'food_type']}
        additional_requirements = self.tm.additional_requirements.copy()
        
        preference_combinations = [
            ['location', 'price_range', 'food_type'],
            ['location', 'price_range'],
            ['location', 'food_type'],
            ['price_range', 'food_type'],
            ['location'],
            ['price_range'],
            ['food_type'],
            []
        ]
        
        for combination in preference_combinations:
            print(f"DEBUG: Trying preference combination: {combination}")
            current_preferences = {k: primary_preferences[k] for k in combination if k in primary_preferences}
            print(f"DEBUG: Current preferences for this iteration: {current_preferences}")
            
            candidates = self.restaurant_lookup.get_candidates(current_preferences)
            print(f"DEBUG: Number of candidates found: {len(candidates)}")
            
            if not candidates.empty:
                candidates = candidates[~candidates['restaurantname'].isin(self.suggested_restaurants)]
                print(f"DEBUG: Number of candidates after filtering suggested restaurants: {len(candidates)}")
                
                if not candidates.empty:
                    selected_restaurant = self.restaurant_lookup.apply_inference_and_select(candidates, additional_requirements)
                    print(f"DEBUG: Selected restaurant: {selected_restaurant}")
                    
                    if isinstance(selected_restaurant, dict):
                        eelf.suggest_specific_restaurant(selected_restaurant, additional_requirements)
                        return
                    else:
                        print(f"DEBUG: No restaurant found matching additional requirements: {additional_requirements}")
                else:
                    print("DEBUG: All candidates have been suggested before")
            else:
                print("DEBUG: No candidates found for this preference combination")
            
            if combination:
                removed_pref = set(primary_preferences.keys()) - set(combination)
                removed_pref = list(removed_pref)[0] if removed_pref else "all primary"
                message = self.get_relaxed_preference_message(removed_pref)
                self.output_message(message)
        
        message = self.get_no_more_restaurants_message()
        self.output_message(message)
        
        self.suggested_restaurants.clear()
        print("DEBUG: Cleared suggested restaurants list")
        
        self.tm.set_state("10. Intermediate (Alternative) State")
        self.tm.speak()

    def get_relaxed_preference_message(self, pref):
        if pref == "all primary":
            if assignment_1c.config.use_formal_language:
                return "I apologize, but I couldn't find a restaurant meeting any of your primary preferences. I'll now search without considering those preferences."
            else:
                return "Sorry, couldn't find anything matching your main preferences. I'll look for any restaurant now."
        else:
            if assignment_1c.config.use_formal_language:
                return f"I apologize, but I couldn't find a restaurant meeting all your preferences. I've adjusted the {pref} requirement to broaden the search."
            else:
                return f"Sorry, couldn't find a perfect match. I've loosened up the {pref} requirement to find more options."

    def get_no_more_restaurants_message(self):
        if assignment_1c.config.use_formal_language:
            return "I apologize, but I couldn't find any more restaurants matching your preferences."
        else:
            return "Oops! No more restaurants match what you're looking for."

    def get_restaurant_suggestion_message(self, restaurant):
        message = f"How about {restaurant['restaurantname']}? "
        details = []
        if 'food' in restaurant:
            details.append(f"It's a {restaurant['food']} restaurant")
        if 'area' in restaurant:
            details.append(f"in the {restaurant['area']} area")
        if 'pricerange' in restaurant:
            details.append(f"with {restaurant['pricerange']} prices")
        
        message += " ".join(details) + "."
        
        if assignment_1c.config.use_formal_language:
            message = f"May I suggest {restaurant['restaurantname']}? " + " ".join(details) + "."
        
        return message

    def output_message(self, message):

        if message is None:
            return
        print("outputting message")

        if assignment_1c.config.all_caps:
            message = message.upper()
        
        self.messages.append(("bot", message))  # Store the message
        self.pending_messages.append(message)  # Add to pending messages
        
        print("self.messages:", self.messages)
        print(message)
        
        if assignment_1c.config.text_to_speech:
            self.tm.tts_engine.say(message)
            self.tm.tts_engine.runAndWait()

    def get_messages(self):
        return self.messages

    def add_user_message(self, message):
        self.messages.append(("user", message))

    def clear_messages(self):
        self.messages = []


    def handle_goodbye(self):
        self.tm.set_state("9. Goodbye")
        self.tm.speak()
        self.tm.dead = True

    def handle_invalid_input(self, context: str):
        clarification = f"I'm sorry, I didn't understand that. Could you please clarify your {context}?" if not assignment_1c.config.all_caps else f"I'M SORRY, I DIDN'T UNDERSTAND THAT. COULD YOU PLEASE CLARIFY YOUR {context.upper()}?"
        self.output_message(clarification)

    def generate_confirmation_prompt(self, pref_key: str, pref_value: str) -> str:
        formal_prompts = {
            'location': f"You mentioned you would like to dine in {pref_value}. Is that correct?",
            'price_range': f"You indicated a price range of {pref_value}. Is that accurate?",
            'food_type': f"You prefer {pref_value} cuisine. Is that correct?"
        }
        informal_prompts = {
            'location': f"You wanna eat in {pref_value}, right?",
            'price_range': f"So, {pref_value} is your budget?",
            'food_type': f"You're into {pref_value} food, yeah?"
        }
        prompt = formal_prompts.get(pref_key, "Is that correct?") if assignment_1c.config.use_formal_language else informal_prompts.get(pref_key, "Is that right?")
        return prompt.upper() if assignment_1c.config.all_caps else prompt

    def generate_ask_preference_prompt(self, pref_key: str) -> str:
        formal_prompts = {
            'location': "Could you please specify the area in which you would like to dine?",
            'price_range': "May I inquire about your preferred price range? (e.g., cheap, moderate, expensive)",
            'food_type': "What type of cuisine do you prefer?"
        }
        informal_prompts = {
            'location': "Which part of town do you wanna eat in?",
            'price_range': "What's your budget? (cheap, moderate, expensive)",
            'food_type': "What kind of food are you into?"
        }
        prompt = formal_prompts.get(pref_key, "Could you please provide more details?") if assignment_1c.config.use_formal_language else informal_prompts.get(pref_key, "Can you give me more info?")
        return prompt.upper() if assignment_1c.config.all_caps else prompt

