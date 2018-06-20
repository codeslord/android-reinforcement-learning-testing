# Test environment
import json
import logging
import os
import random

from src.env.recorda.modelbuilder import ModelBuilder
from state import *

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
        self.q_value = {}  # state|| hash_action : value
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
                    for hash, value in mb.h_event_count.items():
                        key = "{}||{}".format(activity_name, hash).encode('utf-8').strip()
                        self.reward_unvisited_action[key] = value
        logger.info("Initial Q value from recorda")
        logger.info(self.q_value)
        logger.info("Initial state from recorda")
        logger.info([str(state) for state in self.states.values()])

    def is_known_state(self, activity, clickable_actions):
        hash_actions = hash_all_gui_event(clickable_actions)
        hash_object = {
            "activity": activity,
            "actions": hash_actions.keys()
        }
        id_to_compare = hashlib.md5(str(hash_object)).hexdigest()
        if id_to_compare in self.states:
            return self.states[id_to_compare]
        # for s in self.states.values():
        #     if s.activity == activity and equal_hash_actions(hash_actions, s.hash_actions):
        #         known_state = s
        #         print("Found existing state {} - {} actions !!!!!".format(s.activity, len(s.hash_actions)))
        #         if id_to_compare in self.states:
        #             print("state hash validated")
        #         else:
        #             print("state hash problem")
        # print("is_known_state {}".format(datetime.datetime.now() - start))
        return None

    def add_state(self, state):
        self.states[str(state.id)] = state
        self.actions.update(state.hash_actions)
        for key in state.q_value:
            if key in self.q_value:
                state.q_value[key] = self.q_value[key]
            else:
                self.q_value[key] = state.q_value[key]
        return state

    def set_current_state(self, activity, clickable_components):
        state = State(activity, clickable_components)
        if state.id in self.states:
            self.current_state = self.states[state.id]
        else:
            s = self.add_state(state)
            self.current_state = s

    def set_next_state(self, activity, clickable_components):
        state = State(activity, clickable_components)
        if state.id in self.states:
            self.next_state = self.states[state.id]
        else:
            s = self.add_state(state)
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
                # paired = zip(map(operator.itemgetter(0), old_state.hash_actions.values()),
                #              map(operator.itemgetter(0), new_state.hash_actions.values()))
                # shared_items = [(x, y) for (x, y) in paired if x == y]
                shared_items = set(old_state.hash_actions.keys()) & set(new_state.hash_actions.keys())
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
            key = get_qvalue_key(self.current_state, self.current_action)
            reward_key = self.get_reward_key(self.current_state, self.next_state)
            if 'com.android' in self.next_state.activity or 'com.google.android' in self.next_state.activity or 'launcher' in self.next_state.activity or 'mCurrentFocus=null' in self.next_state.activity:
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

    def get_random_state(self):
        return random.choice(self.states.values())
