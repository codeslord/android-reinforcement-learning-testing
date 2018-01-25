# Test environment
import random
from state import *
from simplifier import Simplifier
import os
import json
from modelbuilder import ModelBuilder


DEFAULT_REWARD = 0
RECORDA_WEIGHT = 10

class Environment(object):

    def __init__(self, alpha=1.0, gamma=0.9, recorda_path=None):
        self.states = {}  # state id : state
        self.actions = {}  # hash_action : [sim_action, action]
        self.reward = {}  # old_state_id|new_state_id : value
        self.q_value = {}  # state| hash_action : value
        self.current_state = None
        self.next_state = None
        self.current_action = None
        self.alpha = alpha
        self.gamma = gamma
        self.recorda_actions = {}
        if recorda_path:
            for filename in os.listdir(recorda_path):
                package = recorda_path.split('/')[-3]
                if filename.startswith(package):
                    activity_name = filename[len(package) + 1: -5]
                else:
                    activity_name = filename[0:-5]
                self.add_state(State(activity_name, []))
                with open(os.path.join(recorda_path, filename)) as file:
                    recorda_raw_actions = json.load(file)
                    mb = ModelBuilder(recorda_raw_actions)
                    for hash, value in mb.h_event_freq.items():
                        key = "{}||{}".format(activity_name, hash).encode('utf-8').strip()
                        self.q_value[key] = RECORDA_WEIGHT * value
        print(self.q_value)

    def is_known_state(self, state):
        known_state = None
        for s in self.states.values():
            if s.equal(state):
                known_state = s
                # print("Found existing state {} - {} actions !!!!!".format(s.activity, len(s.actions)))
        return known_state

    def add_state(self, state):
        if not self.is_known_state(state):
            """ How to have an unique id for a view ?"""
            self.states[str(state.id)] = state
            self.actions.update(state.hash_actions)
            for key in state.q_value:
                if key in self.q_value:
                    state.q_value[key] = self.q_value[key]
                    # print("##### found q value from recorda #####")
                else:
                    self.q_value[key] = state.q_value[key]
            # print("Add state")
            # print(state.activity)

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
        key = self.get_reward_key(old_state, new_state)
        if key not in self.reward:
            # if old_state.id == new_state.id:
            #     reward = - 0.01
            reward = DEFAULT_REWARD
            if len(new_state.actions):
                paired = zip(map(operator.itemgetter(0), old_state.hash_actions.values()),
                             map(operator.itemgetter(0), new_state.hash_actions.values()))
                shared_items = [(x, y) for (x, y) in paired if x == y]
                similarity_counter = len(shared_items)
                reward = (len(new_state.hash_actions) - similarity_counter)/float(len(new_state.actions))
            self.reward[key] = reward

    def update_q(self):
        if self.current_state and self.next_state:
            key = get_state_hash_action_key(self.current_state, self.current_action)
            reward_key = self.get_reward_key(self.current_state, self.next_state)
            if self.next_state.activity == 'com.android.systemui.recents.RecentsActivity' or self.next_state.activity == 'com.android.launcher2.Launcher' or self.next_state.activity == "com.jiubang.golauncher.GOLauncher" or self.next_state.activity == 'com.android.launcher3.Launcher' or 'mCurrentFocus=null' in self.next_state.activity:
                value = 0
            # elif key in self.q_value:
                # print(self.q_value[key])
                # print(self.reward[self.get_reward_key(self.current_state, self.next_state)])
                # print(max(list(self.next_state.q_value.values())))
                # value = self.q_value[key] + self.alpha*(self.reward[self.get_reward_key(self.current_state, self.next_state)] + self.gamma*max(list(self.next_state.q_value.values())) - self.q_value[key])
                # value = self.reward[self.get_reward_key(self.current_state, self.next_state)] + self.gamma * max(list(self.next_state.q_value.values()))
            elif len(self.next_state.q_value.values()) > 0:
                # print("NEXT Q VALUE")
                # print(self.next_state.q_value.values())
                # print("CURRENT Q VALUE")
                # print(self.current_state.q_value.values())
                # print("max {}".format(max(list(self.next_state.q_value.values()))))
                # value = DEFAULT_Q + self.alpha * (self.reward[self.get_reward_key(self.current_state, self.next_state)] + self.gamma * max(list(self.next_state.q_value.values())) - DEFAULT_Q)
                value = self.reward[reward_key] + self.gamma * max(list(self.next_state.q_value.values()))
            else:
                value = self.reward[reward_key]
            print("{} - > {}: {} -> {}. Reward {}".format(self.current_state.activity, self.next_state.activity, self.q_value[key] if key in self.q_value else 'None', value, self.reward[reward_key]))
            self.q_value[key] = value
            self.states[str(self.current_state.id)].update_q(self.current_action, value)
            # print("AFTER MODIFIED CURRENT Q VALUE")
            # print(self.current_state.q_value.values())
            # print("AFTER MODIFIED ENV Q VALUE")
            # print(self.states[str(self.current_state.id)].q_value.values())


    def end_episode(self):
        self.current_state = None
        self.current_action = None
        self.next_state = None

    def get_random_state(self):
        return random.choice(self.states.values())
