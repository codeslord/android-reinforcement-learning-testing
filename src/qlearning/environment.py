# Test environment
import random
from state import get_state_component_key, State, DEFAULT_Q

DEFAULT_REWARD = 0.1


class Environment(object):
    states = {}
    actions = {}
    reward = {}
    q_value = {}
    current_state = None
    next_state = None
    current_action = None

    def __init__(self, alpha=1., gamma=0.9):
        self.states = {}
        self.actions = {}
        self.reward = {}
        self.q_value = {}
        self.current_state = None
        self.next_state = None
        self.current_action = None
        self.alpha = alpha
        self.gamma = gamma

    def add_state(self, state):
        if state.activity not in self.states:
            """ How to have an unique id for a view ?"""
            self.states[state.activity] = state
            self.actions[state.activity] = state.actions
            self.q_value.update(state.q_value)
            print("Add state")
            print(state.activity)

    def set_current_state(self, activity, clickable_list):
        if activity in self.states:
            self.current_state = self.states[activity]
        else:
            state = State(activity, clickable_list)
            self.add_state(state)
            self.current_state = state

    def set_next_state(self, activity, clickable_list):
        if activity in self.states:
            self.next_state = self.states[activity]
        else:
            state = State(activity, clickable_list)
            self.add_state(state)
            self.next_state = state

    def get_available_action(self):
        return self.actions[self.current_state.activity]

    def get_reward_key(self, old_state, new_state):
        return "{}:{}".format(old_state.activity, new_state.activity)

    def add_reward(self, old_state, new_state):
        similarity_counter = 0
        for component in new_state.actions:
            if component in old_state.actions:
                similarity_counter += 1
        if len(new_state.actions):
            reward = (len(new_state.actions) - similarity_counter)/len(new_state.actions)
        else:
            reward = DEFAULT_REWARD
        self.reward[self.get_reward_key(old_state, new_state)] = reward

    def update_q(self):
        if self.current_state and self.next_state:
            key = get_state_component_key(self.current_state, self.current_action)
            if key in self.q_value:
                value = self.q_value[key] + self.alpha*(self.reward[self.get_reward_key(self.current_state, self.next_state)] + self.gamma*max(list(self.next_state.q_value.values())))
            else:
                value = DEFAULT_Q + self.alpha*(self.reward[self.get_reward_key(self.current_state, self.next_state)] + self.gamma*max(list(self.next_state.q_value.values())))
            self.q_value[key] = value
            self.current_state.update_q(self.current_action, value)
            print("Updating q value for {} = {}".format(key, value))

    def end_episode(self):
        self.current_state = None
        self.current_action = None
        self.next_state = None

    def get_random_state(self):
        return random.choice(self.states.values())