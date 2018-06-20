import time
import random
from guiobserver import GuiObserver
from executor import Executor
from recorda.dataprocessor import DataProcessor

"""
State is a tuple (activity_name, tuple of actions)
action is a tuple (resource_id, event_type, bounds, text or "")
"""


class Environment(object):
    device = None
    package = None
    current_state = None
    next_state = None
    visited_states = []
    recorda_reward = {}
    observer = None
    executor = None

    def __init__(self, device, package, recorda=None):
        self.device = device
        self.observer = GuiObserver(device)
        self.executor = Executor(device)
        self.package = package
        if recorda:
            dp = DataProcessor(package)
            dp.process_all_events()
            self.recorda_reward = dp.get_recorda_reward()

    def observe_current_state(self):
        self.observer.dump_gui(self.package)
        state = (self.observer.activity, str(self.observer.actionable_events))
        return state

    def observe_next_state(self, action):
        self.executor.perform_action(action)
        time.sleep(0.2)
        next_state = self.observe_current_state()
        return next_state

    def finish_transition(self):
        self.current_state = self.next_state
        self.next_state = None
        self.visited_states.append(self.next_state)

    def get_reward(self):
        if self.next_state and self.current_state:
            current_actions = self.current_state[1]
            next_actions = self.next_state[1]
            shared_items = set(current_actions) & set(next_actions)
            reward = (len(next_actions) - len(shared_items))/float(len(next_actions))
        else:
            reward = 0
        # TODO return reward from recorda
        return reward

    def get_random_state(self):
        return random.choice(self.visited_states)
