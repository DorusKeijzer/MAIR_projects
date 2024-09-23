class State:
    """Keeps track of one state and the states it transitions to. When initialzing states, it is easiest to start from the final state"""

    def __init__(self, name: str, transitions={}, terminal=False, optional=False):
        """A transition is a tuple consisting of 1. conditions 2. the state to transition to"""
        self.name = name
        self.transitions = transitions
        self.terminal = terminal  # true for the final node
        self.prompt = ""  # which question the agent will ask in this state
        # allows agent to skp questions that might have already been answered
        self.optional = optional
        self.make_suggestion = False  # whether the agent should make a suggestion here

    def __repr__(self) -> str:
        return self.name


class TransitionManager:
    """Manages the state transitions: takes a number of states and keeps track of the current state"""

    def __init__(self, states, starting_state=None):
        self.preferences = {"food_type": None,
                            "price_range":  None, "location": None}
        if states == []:
            raise Exception("States cannot be empty")
        self.states = states

        if starting_state is None:
            self.current_state = self.states[0]
        else:
            self.current_state = starting_state
        # will go true if agent reaches a terminal state
        self.dead = False

    def speak(self):
        """The agent says the prompt associated with this state"""
        print(self.current_state.prompt)

    def set_state(self, state):
        """Sets the current state to one of the valid states"""
        if state not in self.states:
            raise Exception(f"{state} is not a valid state")
        self.current_state = state

    def update_preferences(self, key: str, value: str):
        if key not in self.preferences.keys():
            raise KeyError("Key must be food_type, price_range, location")

        self.preferences[key] = value

    def transition(self, dialogue_act):
        """If conditions are met, transitions to the next state based on the current dialogue act"""
        if dialogue_act not in self.current_state.transitions.keys():
            print("I am sorry, I don't understand. Rephrase your answer")
            return False
        conditions,  new_state,  = self.current_state.transitions[dialogue_act]

        if self._conditions_met(conditions):

            self.set_state(new_state)
            # attempts to bypass the current state if conditions are already met
            while self._bypass_state():
                pass
            # kills agent if state is terminal
            if new_state.terminal:
                self.dead = True
            return True
        return False

    def _conditions_met(self, conditions):
        """Returns true if all conditions are met, else shortcuts to false"""
        for condition in conditions:
            if self.preferences[condition] is None:
                return False
        return True

    def _bypass_state(self):
        for key in self.current_state.transitions.keys():
            conditions, new_state = self.current_state.transitions[key]
            if self.current_state.optional and self._conditions_met(conditions):
                self.set_state(new_state)
                return True
        return False

    def __repr__(self):
        if self.current_state is None:
            return "No current state"
        else:
            return self.current_state.name


if __name__ == "__main__":
    suggest = State("Suggest restaurant")
    ask_area = State("Ask Area", transitions={"reply_area": suggest})
    welcome = State("Welcome", transitions={
        "other": ask_area, "express_area": suggest})

    tm = TransitionManager([suggest, ask_area, welcome], welcome)
    print(tm)
    tm.transition("other")
    print(tm)
    tm.transition("reply_area")
    print(tm)
