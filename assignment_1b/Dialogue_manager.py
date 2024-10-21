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

    def start_conversation(self):
        """Start the conversation and return the initial message."""
        print("starting conversation")
        if not self.conversation_started:
            self.conversation_started = True
            initial_response = self.tm.speak()
            self.output_message(initial_response)
            return {"response": initial_response}
        else:
            return {"response": "Conversation already started."}
    def continue_conversation(self, user_input):
        """Continue the conversation based on user input."""
        print(f"Continue the conversation based on user input: {user_input}")
        if not self.conversation_started:
            return {"response": "Conversation not started. Please start the conversation first."}

        if self.tm.dead or self.tm.current_state.terminal:
            return {"response": "Conversation ended."}

        self.process_input(user_input)
        response = self.tm.speak()
        self.output_message(response)
        return {"response": response}

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
        extracted_prefs, _ = self.preference_extractor.extract_preferences(user_input)

        if assignment_1c.config.ask_preference_confirmation:
            self.preferences_to_confirm = list(extracted_prefs.keys())
            self.extracted_prefs = extracted_prefs
            self.confirm_next_preference()
        else:
            self.tm.preferences.update(extracted_prefs)
            self.move_to_next_state()

    def confirm_next_preference(self):
        if self.preferences_to_confirm:
            pref_key = self.preferences_to_confirm.pop(0)
            pref_value = self.extracted_prefs[pref_key]
            prompt = self.generate_confirmation_prompt(pref_key, pref_value)
            self.tm.pending_pref_key = pref_key
            self.tm.pending_pref_value = pref_value
            self.tm.set_state("Confirmation", prompt=prompt)
            self.tm.speak()
        else:
            self.tm.preferences.update(self.extracted_prefs)
            self.move_to_next_state()

    def move_to_next_state(self):
        missing_preferences = [key for key in ['location', 'price_range', 'food_type'] if self.tm.preferences.get(key) is None]

        if not missing_preferences:
            self.tm.set_state("5. Collect Candidates")
        else:
            next_state = self.determine_next_state(self.tm.preferences)
            self.tm.set_state(next_state)
        self.tm.speak()

    def handle_confirmation(self, user_input: str, dialogue_act: str):
        if dialogue_act in ['affirm', 'yes', 'confirm']:
            pref_key = self.tm.pending_pref_key
            pref_value = self.tm.pending_pref_value
            self.tm.update_preferences(pref_key, pref_value)
            self.confirm_next_preference()
        elif dialogue_act in ['deny', 'no', 'negate']:
            pref_key = self.tm.pending_pref_key
            self.tm.update_preferences(pref_key, None)
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
        return "5. Collect Candidates"

    def handle_collect_candidates(self):
        self.tm.candidate_restaurants = self.restaurant_lookup.get_candidates(self.tm.preferences)
        self.tm.set_state("6. Ask Additional Requirements")
        self.tm.speak()

    def handle_ask_additional_requirements(self, user_input: str, dialogue_act: str):
        if dialogue_act in ["deny", "negate"]:
            self.suggest_restaurant(allow_alternatives=False)
            self.tm.set_state("7. Suggest Restaurant")
            self.tm.speak()
        elif dialogue_act in ["affirm", "request", "remove", "confirm", "ack"]:
            additional_requirements, _ = self.preference_extractor.extract_additional_requirements(user_input)
            if isinstance(additional_requirements, dict) and additional_requirements:
                self.tm.additional_requirements.update(additional_requirements)
            self.suggest_restaurant(allow_alternatives=True)
        else:
            self.handle_invalid_input("additional requirements")

    def suggest_restaurant(self, allow_alternatives=False):
        candidates = self.restaurant_lookup.get_candidates(self.tm.preferences)
        selected_restaurant_data = self.restaurant_lookup.apply_inference_and_select(candidates, self.tm.additional_requirements)

        if isinstance(selected_restaurant_data, str):
            if allow_alternatives:
                no_match_message = "No matching restaurants found. Suggesting alternatives."
                self.output_message(no_match_message)

                selected_restaurant_data = self.restaurant_lookup.apply_inference_and_select(candidates, {})
                if isinstance(selected_restaurant_data, str):
                    no_alternatives_message = "No suitable alternatives found."
                    self.output_message(no_alternatives_message)
                else:
                    self.suggest_specific_restaurant(selected_restaurant_data, {})
            else:
                message = "No matching restaurants found." if not assignment_1c.config.use_formal_language else "Regrettably, no restaurants meet your preferences."
                self.output_message(message)
        else:
            self.suggest_specific_restaurant(selected_restaurant_data, self.tm.additional_requirements)

        self.tm.set_state("10. Intermediate (Alternative) State")
        self.tm.speak()

    def suggest_specific_restaurant(self, selected_restaurant_data, requirements):
        restaurant_name = selected_restaurant_data['restaurant']['restaurantname']
        if restaurant_name not in self.suggested_restaurants:
            self.suggested_restaurants.add(restaurant_name)
            reasoning = self.restaurant_lookup.generate_reasoning(selected_restaurant_data, requirements)
            if assignment_1c.config.use_formal_language:
                message = f"Based on your preferences, I recommend {restaurant_name}. {reasoning}"
            else:
                message = f"How about {restaurant_name}? {reasoning}"
            
            self.output_message(message)

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
        prompt = "Would you like to see an alternative restaurant recommendation?" if assignment_1c.config.use_formal_language else "Want to see another restaurant option?"
        self.output_message(prompt)

        if dialogue_act in ['affirm', 'yes', 'alternative', 'another option']:
            self.suggest_alternative_restaurant()
        elif dialogue_act in ['deny', 'no', 'negate', 'bye', 'thankyou', 'thank you']:
            self.handle_goodbye()
        else:
            self.handle_invalid_input("intermediate state")

    def suggest_alternative_restaurant(self):
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
            current_preferences = {k: primary_preferences[k] for k in combination if k in primary_preferences}
            current_preferences.update(additional_requirements)
            
            candidates = self.restaurant_lookup.get_candidates(current_preferences)
            candidates = candidates[~candidates['restaurantname'].isin(self.suggested_restaurants)]
            
            if not candidates.empty:
                self.suggest_from_candidates(candidates)
                return
            
            if combination:
                removed_pref = set(primary_preferences.keys()) - set(combination)
                removed_pref = list(removed_pref)[0] if removed_pref else "all primary"
                message = self.get_relaxed_preference_message(removed_pref)
                self.output_message(message)
        
        message = self.get_no_more_restaurants_message()
        self.output_message(message)
        
        self.suggested_restaurants.clear()
        
        self.tm.set_state("10. Intermediate (Alternative) State")
        self.tm.speak()

    def suggest_from_candidates(self, candidates):
        if candidates.empty:
            message = self.get_no_more_restaurants_message()
        else:
            selected_restaurant = candidates.sample(n=1).iloc[0]
            self.suggested_restaurants.add(selected_restaurant['restaurantname'])
            message = self.get_restaurant_suggestion_message(selected_restaurant)
        
        self.output_message(message)

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
        print("outputting message")
        if assignment_1c.config.all_caps:
            message = message.upper()
        self.messages.append(("bot", message))  # Store the message
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
