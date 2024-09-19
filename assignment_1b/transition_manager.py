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

    def __init__(self, states, starting_state=None):
        if states == []:
            raise Exception("States cannot be empty")
        self.states = states

        if starting_state is None:
            self.current_state = self.states[0]
        else:
            self.current_state = starting_state

    def set_state(self, state):
        """Sets the current state to one of the valid states"""
        if state not in self.states:
            raise Exception("Not a valid state")
        self.current_state = state

    def register_state(self, state: State):
        """Adds a new state"""
        self.states.append(state)

    def transition(self, dialogue_act):
        """Transitions to the next state based on the current dialogue act"""
        if dialogue_act not in self.current_state.transitions.keys():
            # defaults to other in case there is no transition specified for this dialogue act
            dialogue_act = "other"
        self.set_state(self.current_state.transitions[dialogue_act])

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
