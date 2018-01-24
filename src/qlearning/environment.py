# Test environment
import random
from state import *
from simplifier import Simplifier

DEFAULT_REWARD = 0.1


class Environment(object):

    def __init__(self, alpha= 1.0, gamma=0.9):
        self.states = {}  # state id : state
        self.actions = {}  # hash_action : action
        self.reward = {}  # old_state|new_state : value
        self.q_value = {}  # state| hash_action : value
        self.current_state = None
        self.next_state = None
        self.current_action = None
        self.alpha = alpha
        self.gamma = gamma

    def is_known_state(self, state):
        known_state = None
        for s in self.states.values():
            if s.equal(state):
                known_state = s
                print("Found existing state !!!!!")
        return known_state

    def add_state(self, state):
        if not self.is_known_state(state):
            """ How to have an unique id for a view ?"""
            self.states[state.id] = state
            self.actions.update(hash_all_gui_event(state.actions))
            self.q_value.update(state.q_value)
            print("Add state")
            print(state.activity)

    def set_current_state(self, activity, clickable_list):
        s = State(activity, clickable_list)
        known_state = self.is_known_state(s)
        if known_state:
            self.current_state = known_state
        else:
            self.add_state(s)
            self.current_state = s

    def set_next_state(self, activity, clickable_list):
        s = State(activity, clickable_list)
        known_state = self.is_known_state(s)
        if known_state:
            self.next_state = known_state
        else:
            self.add_state(s)
            self.next_state = s

    def get_available_action(self):
        return self.current_state.hash_actions

    def get_reward_key(self, old_state, new_state):
        return "{}:{}".format(old_state.id, new_state.id)

    def add_reward(self, old_state, new_state):
        paired = zip(map(operator.itemgetter(0), old_state.hash_actions.values()),
                     map(operator.itemgetter(0), new_state.hash_actions.values()))
        shared_items = [(x, y) for (x, y) in paired if x == y]
        similarity_counter = len(shared_items)
        # for component in new_state.actions:
        #     if component in old_state.actions:
        #         similarity_counter += 1
        if len(new_state.actions):
            reward = (len(new_state.actions) - similarity_counter)/float(len(new_state.actions))
        else:
            reward = DEFAULT_REWARD
        self.reward[self.get_reward_key(old_state, new_state)] = reward

    def update_q(self):
        if self.current_state and self.next_state:
            key = get_state_hash_action_key(self.current_state, self.current_action)
            if key in self.q_value:
                print(self.q_value[key])
                print(self.reward[self.get_reward_key(self.current_state, self.next_state)])
                print(max(list(self.next_state.q_value.values())))
                value = self.q_value[key] + self.alpha*(self.reward[self.get_reward_key(self.current_state, self.next_state)] + self.gamma*max(list(self.next_state.q_value.values())))
            else:
                value = DEFAULT_Q + self.alpha * (self.reward[self.get_reward_key(self.current_state, self.next_state)] + self.gamma * max(list(self.next_state.q_value.values())))
            self.q_value[key] = value
            self.current_state.update_q(self.current_action, value)
            print("Updating q value for {} = {}".format(key, value))

    def end_episode(self):
        self.current_state = None
        self.current_action = None
        self.next_state = None

    def get_random_state(self):
        return random.choice(self.states.values())
