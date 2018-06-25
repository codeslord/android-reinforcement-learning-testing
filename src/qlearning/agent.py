# Test environment
import json
import logging
import os
import random
import operator
import pprint

pp = pprint.PrettyPrinter(indent=4)
logging.basicConfig(filename='all.log', level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_Q = 0


class Agent(object):
    def __init__(self, alpha=1.0, gamma=0.9, epsilon=0.8):
        self.q_value = {}  # {state:{action:value}}
        self.alpha = alpha #TODO change the formular to take into account alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def add_state(self, state):
        self.q_value[state] = {}
        for action in state[1]:
            self.q_value[state][action] = DEFAULT_Q

    def select_next_action(self, current_state, epsilon):
        if current_state not in self.q_value:
            self.add_state(current_state)
        r = random.uniform(0.0, 1.0)
        if not current_state[1]:
            logger.info('No action available to select!')
            return None
        else:
            if r < epsilon:
                #select randomly with probability epsilon
                action = random.choice(current_state[1])
                logger.info('Select randomly')
                return action
            else:
                #select highest q with probability 1-epsilon
                max_q_action = max(self.q_value.iteritems(), key=operator.itemgetter(1))[0]
                logger.info("Select action with highest q value")
                return max_q_action

    def update_q(self, current_state, action, reward, next_state):
        if current_state in self.q_value and action in self.q_value[current_state]:
            if next_state in self.q_value:
                value = reward + self.gamma * max(list(self.q_value[next_state].values()))
            else:
                value = reward
            logger.info("{} - > {}: {} -> {}. Reward {}".format(current_state[0], next_state[0] if next_state else "Out of app", self.q_value[current_state][action], value, reward))
            self.q_value[current_state][action] = value
        else:
            self.add_state(current_state)
