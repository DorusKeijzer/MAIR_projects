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
        self.optional = optional  # Allows agent to skip questions that might have already been answered
        self.make_suggestion = False  # Whether the agent should make a suggestion here
        
    def __repr__(self) -> str:
        return self.name


class TransitionManager:
    """Manages the state transitions and keeps track of the current state."""

    def __init__(self, states, starting_state=None):
        """
        :param states: List of State objects.
        :param starting_state: The initial state to start from.
        """
        self.preferences = {"food_type": None, "price_range": None, "location": None}
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

    def speak(self):
        """The agent says the prompt associated with the current state."""
        output = self.current_state.prompt
        if assignment_1c.config.all_caps:
            output = output.upper()
        print(output)

    def set_state(self, state):
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

    def update_preferences(self, key: str, value: str):
        """Updates the user's preferences."""
        if key not in self.preferences.keys():
            raise KeyError("Key must be 'food_type', 'price_range', or 'location'")
        self.preferences[key] = value

    def transition(self, dialogue_act):
        """Transitions to the next state based on the dialogue act and conditions."""
        if dialogue_act not in self.current_state.transitions.keys():
            print("I'm sorry, I don't understand. Could you please rephrase?")
            return False
        conditions, new_state = self.current_state.transitions[dialogue_act]

        if self._conditions_met(conditions):
            self.set_state(new_state)
            # Attempts to bypass the current state if conditions are already met
            while self._bypass_state():
                pass
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

    def _bypass_state(self):
        """Bypasses optional states if conditions are already met."""
        for dialogue_act in self.current_state.transitions.keys():
            conditions, next_state = self.current_state.transitions[dialogue_act]
            if self.current_state.optional and self._conditions_met(conditions):
                self.set_state(next_state)
                return True
        return False

    def __repr__(self):
        return self.current_state.name if self.current_state else "No current state"
