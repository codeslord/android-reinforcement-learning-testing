# Test environment
import random
from state import *
from simplifier import Simplifier
import os
import json
from modelbuilder import ModelBuilder
import logging
import pprint
pp = pprint.PrettyPrinter(indent=4)
logging.basicConfig(filename='all.log', level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_REWARD = 0
RECORDA_WEIGHT = 10

class Agent(object):

    def __init__(self, alpha=1.0, gamma=0.9, recorda_path=None):
        self.states = {}  # state id : state
        self.actions = {}  # hash_action : [sim_action, action]
        self.reward = {}  # old_state_id|new_state_id : value
        self.reward_unvisited_action = {} # state| hash_action : value -> count how many times this action has been executed. Same key as q value
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
                self.add_state(activity_name, [])
                with open(os.path.join(recorda_path, filename)) as file:
                    recorda_raw_actions = json.load(file)
                    mb = ModelBuilder(recorda_raw_actions)
                    for hash, value in mb.h_event_freq.items():
                        key = "{}||{}".format(activity_name, hash).encode('utf-8').strip()
                        self.q_value[key] = RECORDA_WEIGHT * value
                    for hash, value in mb.h_event_count.items():
                        key = "{}||{}".format(activity_name, hash).encode('utf-8').strip()
                        self.reward_unvisited_action[key] = value
        pp.pprint(self.q_value)
        pp.pprint([str(state) for state in self.states.values()])

    def is_known_state(self, activity, clickable_actions):
        known_state = None
        hash_action = hash_all_gui_event(clickable_actions)
        for s in self.states.values():
            if s.activity == activity and equal_hash_actions(hash_action, s.hash_actions):
                known_state = s
                # print("Found existing state {} - {} actions !!!!!".format(s.activity, len(s.hash_actions)))
        return known_state

    """ !!!!! Always call is_known_state before this"""
    def add_state(self, activity, clickable_components):
        state = State(activity, clickable_components)
        self.states[str(state.id)] = state
        self.actions.update(state.hash_actions)
        for key in state.q_value:
            if key in self.q_value:
                state.q_value[key] = self.q_value[key]
            else:
                self.q_value[key] = state.q_value[key]
        return state

    def set_current_state(self, activity, clickable_components):
        known_state = self.is_known_state(activity, clickable_components)
        if known_state:
            self.current_state = known_state
        else:
            s = self.add_state(activity, clickable_components)
            self.current_state = s

    def set_next_state(self, activity, clickable_components):
        known_state = self.is_known_state(activity, clickable_components)
        if known_state:
            self.next_state = known_state
        else:
            s = self.add_state(activity, clickable_components)
            self.next_state = s

    def get_available_action(self):
        return self.current_state.hash_actions

    def get_reward_key(self, old_state, new_state):
        return "{}:{}".format(old_state.id, new_state.id)

    def add_reward(self, old_state, new_state):
        key = self.get_reward_key(old_state, new_state)
        if key not in self.reward:
            reward = DEFAULT_REWARD
            if len(new_state.hash_actions):
                paired = zip(map(operator.itemgetter(0), old_state.hash_actions.values()),
                             map(operator.itemgetter(0), new_state.hash_actions.values()))
                shared_items = [(x, y) for (x, y) in paired if x == y]
                similarity_counter = len(shared_items)
                reward = (len(new_state.hash_actions) - similarity_counter)/float(len(new_state.hash_actions))
            self.reward[key] = reward

    def add_reward_unvisited_action(self):
        if self.current_action and self.current_state:
            key = "{}||{}".format(self.current_state.activity, self.current_action).encode('utf-8').strip()
            if key in self.reward_unvisited_action:
                self.reward_unvisited_action[key] += 1
            else:
                self.reward_unvisited_action[key] = 1

    def get_reward_unvisited_action(self):
        if self.current_action and self.current_state:
            key = "{}||{}".format(self.current_state.activity, self.current_action).encode('utf-8').strip()
            return 1/float(self.reward_unvisited_action[key] + 1)  # avoid division by 0
        return 0

    def update_q(self):
        if self.current_state and self.next_state:
            key = get_state_hash_action_key(self.current_state, self.current_action)
            reward_key = self.get_reward_key(self.current_state, self.next_state)
            if self.next_state.activity == 'com.android.systemui.recents.RecentsActivity' or self.next_state.activity == 'com.android.launcher2.Launcher' or self.next_state.activity == "com.jiubang.golauncher.GOLauncher" or self.next_state.activity == 'com.android.launcher3.Launcher' or 'mCurrentFocus=null' in self.next_state.activity:
                value = 0
            elif len(self.next_state.q_value.values()) > 0:
                value = self.reward[reward_key] + self.get_reward_unvisited_action() + self.gamma * max(list(self.next_state.q_value.values()))
            else:
                value = self.reward[reward_key] + self.get_reward_unvisited_action()
            logger.info("{} - > {}: {} -> {}. Reward {} and {}".format(self.current_state.activity, self.next_state.activity, self.q_value[key] if key in self.q_value else 'None', value, self.reward[reward_key], self.get_reward_unvisited_action()))
            self.q_value[key] = value
            self.states[str(self.current_state.id)].update_q(self.current_action, value)

    def reset(self):
        self.current_state = None
        self.current_action = None
        self.next_state = None

    def get_random_state(self):
        return random.choice(self.states.values())
