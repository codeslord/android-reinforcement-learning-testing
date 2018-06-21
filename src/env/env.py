import random
import time
import logging
import subprocess
from executor import Executor
from guiobserver import GuiObserver
from dataprocessor import DataProcessor


"""
State is a tuple (activity_name, tuple of actions)
action is a tuple (resource_id, event_type, bounds, text or "")
"""

#TOD handle out of app

DEFAULT_REWARD = 0
RECORDA_WEIGHT = 10

logging.basicConfig(filename='all.log', level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class Environment(object):
    device = None
    package = None
    current_state = None
    next_state = None
    visited_states = None
    recorda_reward = {}
    observer = None
    executor = None

    def __init__(self, device, package, recorda=None):
        self.device = device
        self.observer = GuiObserver(device)
        self.executor = Executor(device)
        self.package = package
        self.visited_states = set()
        if recorda:
            dp = DataProcessor(package)
            dp.process_all_events()
            self.recorda_reward = dp.get_recorda_reward()

    def observe_current_state(self):
        self.observer.dump_gui(self.package)
        state = (self.observer.activity, self.observer.actionable_events)
        return state

    def transition_to_next_state(self, action):
        self.executor.perform_action(action)
        time.sleep(0.2)
        next_state = self.observe_current_state()
        if self.is_out_of_app(next_state[0]):
            self.back_to_app()
            self.next_state = None
            self.current_state = self.observe_current_state()
            return None
        self.next_state = next_state
        return next_state

    def set_current_state(self):
        self.current_state = self.observe_current_state()

    def finish_transition(self):
        self.visited_states.add(self.next_state)
        logger.info("Number of visited states: " + str(len(self.visited_states)))
        self.current_state = self.next_state
        self.next_state = None

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
        return random.sample(self.visited_states, 1)[0]

    def is_out_of_app(self, activity):
        """Check is out of app."""
        if self.package in activity:
            return False
        else:
            return True

    def back_to_app(self):
        """Go back."""
        logger.info('backtoapp')
        subprocess.call(['adb', 'shell', 'monkey', '-p', self.package, '-c', 'android.intent.category.LAUNCHER', '1'])

    def jump_to_activity(self, activity):
        output = subprocess.check_output(['adb', 'shell', 'am', 'start', '-n', '{}/{}'.format(self.package, activity)])
        return output
