# assignment_1b/transition_manager.py

import pyttsx3
import assignment_1c.config

class State:
    """Keeps track of one state and the states it transitions to."""

    def __init__(self, name: str, transitions=None, terminal=False, optional=False):
        """
        :param name: Name of the state.
        :param transitions: Dictionary mapping dialogue acts to (conditions, next_state).
        :param terminal: Whether this state is a terminal state.
        :param optional: Whether this state can be bypassed if conditions are already met.
        """
        if transitions is None:
            transitions = {}
        self.name = name
        self.transitions = transitions
        self.terminal = terminal  # True for the final node
        self.prompt = ""  # The question the agent will ask in this state
        self.optional = optional

    def __repr__(self) -> str:
        return self.name


class TransitionManager:
    """Manages the state transitions and keeps track of the current state."""

    def __init__(self, states, starting_state=None):
        """
        :param states: List of State objects.
        :param starting_state: The initial state to start from.
        """
        self.preferences = {"food_type": None,
                            "price_range": None, "location": None}
        if not states:
            raise Exception("States cannot be empty")
        self.states = states

        if starting_state is None:
            self.current_state = self.states[0]
        else:
            self.current_state = starting_state
        self.additional_requirements = {}
        self.candidate_restaurants = []
        self.dead = False  # Will become True if agent reaches a terminal state
        self.tts_engine = pyttsx3.init()

        self.pending_pref_key = None
        self.pending_pref_value = None

    def speak(self):
        """The agent says the prompt associated with the current state."""
        output = self.current_state.prompt
        if self.current_state.name == "Confirmation":
            # Dynamic prompts are set in DialogueManager before calling speak()
            output = self.current_state.prompt
        if assignment_1c.config.all_caps and self.current_state.name != "Confirmation":
            output = output.upper()
        if output:
            print(output)
            if assignment_1c.config.text_to_speech:
                self.tts_engine.say(output)
                self.tts_engine.runAndWait()
            return output

    def set_state(self, state, prompt=None):
        """Sets the current state to one of the valid states."""
        if isinstance(state, str):
            # Find the state with the given name
            matching_states = [s for s in self.states if s.name == state]
            if not matching_states:
                raise Exception(f"State '{state}' is not a valid state")
            state = matching_states[0]
        if state not in self.states:
            raise Exception(f"{state} is not a valid state")
        self.current_state = state
        # If a prompt is provided (for Confirmation), set it
        if prompt:
            self.current_state.prompt = prompt
        # Set terminal flag if the current state is terminal
        if self.current_state.terminal:
            self.dead = True

    def update_preferences(self, key: str, value: str):
        """Updates the user's preferences."""
        if key not in self.preferences.keys():
            raise KeyError(
                "Key must be 'food_type', 'price_range', or 'location'")
        
        # Check if preference change is allowed
        if not assignment_1c.config.allow_preference_change and self.preferences[key] is not None:
            message = f"Preference for {key.replace('_', ' ')} is already set and cannot be changed."
            if assignment_1c.config.all_caps:
                message = message.upper()
            print(message)
            if assignment_1c.config.text_to_speech:
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
            return  # Do not update the preference if it's already set and changes are not allowed
        
        self.preferences[key] = value

    def transition(self, dialogue_act):
        """Transitions to the next state based on the dialogue act and conditions."""
        if dialogue_act not in self.current_state.transitions.keys():
            # Handle unexpected dialogue acts gracefully
            clarification = "I'm sorry, I didn't understand that. Could you please clarify?"
            if assignment_1c.config.all_caps:
                clarification = clarification.upper()
            print(clarification)
            if assignment_1c.config.text_to_speech:
                self.tts_engine.say(clarification)
                self.tts_engine.runAndWait()
            return False
        conditions, new_state = self.current_state.transitions[dialogue_act]

        if self._conditions_met(conditions):
            self.set_state(new_state)
            # Sets dead to True if the current state is terminal
            if self.current_state.terminal:
                self.dead = True
            return True
        return False

    def _conditions_met(self, conditions):
        """Checks if all required conditions are met."""
        for condition in conditions:
            if self.preferences.get(condition) is None:
                return False
        return True

    def __repr__(self):
        return self.current_state.name if self.current_state else "No current state"
