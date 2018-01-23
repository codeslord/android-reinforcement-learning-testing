# Test environment
from state import get_state_component_key

class Environment(object):
    states = {}
    actions = {}
    reward = {}
    q_value = {}
    current_state = None
    next_state = None
    current_action = None
    alpha = 1.
    gamma = 0.9

    def __init__(self):
        self.states = {}
        self.actions = {}
        self.reward = {}
        self.q_value = {}
        self.current_state = None
        self.next_state = None
        self.current_action = None

    def add_state(self, state):
        if state.activity not in self.states:
            self.states[state.activity] = state
            self.actions[state.activity] = state.actions
            self.q_value.update(state.q_value)
            print("Add state")
            print(state.activity)

    def set_current_state(self, state):
        self.add_state(state)
        self.current_state = state

    def get_available_action(self):
        return self.actions[self.current_state.activity]

    def get_reward_key(self, old_state, new_state):
        return "{}:{}".format(old_state.activity, new_state.activity)

    def add_reward(self, old_state, new_state):
        similarity_counter = 0
        for component in new_state.actions:
            if component in old_state.actions:
                similarity_counter += 1
        reward = (len(new_state.actions) - similarity_counter)/len(new_state.actions)
        self.reward[self.get_reward_key(old_state, new_state)] = reward

    def update_q(self):
        if self.current_state and self.next_state:
            key = get_state_component_key(self.current_state, self.current_action)
            if key in self.q_value:
                self.q_value[key] += self.reward[self.get_reward_key(self.current_state, self.next_state)] + max(list(self.next_state.q_value.values()))
            else:
                self.q_value[key] = 0.5 + self.reward[self.get_reward_key(self.current_state, self.next_state)] + max(list(self.next_state.q_value.values()))
        print("Updating q value for {} = {}".format(key, self.q_value[key]))

    def initialize_from_recorda(self, raw_events):
        pass