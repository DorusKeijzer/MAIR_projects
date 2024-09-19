class State:
    """Keeps track of one state and the states it transitions to. When initialzing states, it is easiest to start from the final state"""

    def __init__(self, name: str, transitions={}):
        self.name = name
        self.transitions = transitions

    def __repr__(self) -> str:
        return self.name

    def register_transition(self, dialogue_act: str, next_state: 'State'):
        """Adds a new transition"""
        print(f"Registering transition from {
              self} to {next_state} when {dialogue_act}")
        self.transitions[dialogue_act] = next_state


class TransitionManager:
    """Manages the state transitions: takes a number of states and keeps track of the current state"""

    def __init__(self, states=[], currentstate=None):
        self.states = states
        self.current_state = currentstate

    def set_state(self, state):
        """Sets the current state to one of the valid states"""
        if state not in self.states:
            raise Exception("Not a valid state")
        self.current_state = state

    def register_state(self, state: State):
        """Adds a new state"""
        self.states.append(state)

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
