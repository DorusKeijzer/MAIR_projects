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

    def __init__(self, states, initial_state):
        self.states = {state.name: state for state in states}
        self.current_state = initial_state
        self.preferences = {}
        self.additional_requirements = {}
        self.candidate_restaurants = None
        self.dead = False
        self.tts_engine = pyttsx3.init()
        self.pending_pref_key = None
        self.pending_pref_value = None
        print(f"DEBUG: TransitionManager initialized with initial state: {initial_state.name}")

    def set_state(self, state_name, prompt=None):
        print(f"DEBUG: Attempting to set state to: {state_name}")
        if state_name in self.states:
            self.current_state = self.states[state_name]
            if prompt:
                self.current_state.prompt = prompt
            print(f"DEBUG: State set to: {self.current_state.name}")
        else:
            print(f"DEBUG: Error - State {state_name} not found")

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


    def update_preferences(self, key, value):
        print(f"DEBUG: Updating preferences - {key}: {value}")
        self.preferences[key] = value
        print(f"DEBUG: Updated preferences: {self.preferences}")

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
            self.set_state(new_state.name)
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
