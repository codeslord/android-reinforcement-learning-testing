import random
import time
import logging
import subprocess
from .executor import Executor
from .guiobserver import GuiObserver
from .dataprocessor import DataProcessor


"""
State is a tuple (activity_name, tuple of actions)
action is a tuple (resource_id, event_type, bounds, text or "")
"""

#TOD handle out of app

DEFAULT_REWARD = 0
RECORDA_WEIGHT = 10
MAX_CLICK = 2

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
        self.observer = GuiObserver(package, device)
        self.executor = Executor(device)
        self.package = package
        self.visited_states = {}
        if recorda:
            dp = DataProcessor(package)
            dp.process_all_events()
            self.recorda_reward = dp.get_recorda_reward()
            logger.info(self.recorda_reward)

    def observe_current_state(self):
        self.observer.dump_gui()
        state = (self.observer.activity, self.observer.app_actions)
        return state

    def transition_to_next_state(self, action):
        if not action:
            # No action to select
            self.device.press.back()
            # self.kill_app()
            # self.back_to_app()
            #subprocess.call(['adb', 'shell', 'monkey', '-p', self.package, '1'])
        else:
            self.executor.perform_action(action)
        time.sleep(0.2)
        next_state = self.observe_current_state()
        # Check if next state is out of app
        if self.is_out_of_app(next_state[0]):
            self.handle_out_of_app(MAX_CLICK)
            self.next_state = None
            self.current_state = self.observe_current_state()
            return None
        elif "Application Error" in next_state[0]:
            self.kill_app()
            return None
        self.next_state = next_state
        # If next state is out of app, return None
        return next_state

    def set_current_state(self):
        self.current_state = self.observe_current_state()

    def finish_transition(self):
        if self.next_state in self.visited_states:
            self.visited_states[self.next_state] += 1
        else:
            self.visited_states[self.next_state] = 1
        self.current_state = self.next_state
        self.next_state = None

    def get_count_reward(self):
        if self.next_state in self.visited_states and self.visited_states[self.next_state] != 0:
            # logger.info("Count reward {}".format(1/float(self.visited_states[self.next_state])))
            return 1/float(self.visited_states[self.next_state])
        return 0

    def get_recorda_reward(self, action):
        reward = 0
        if action:
            simplified_action = action[:-1]
            key = (self.current_state[0], simplified_action)
            if key in self.recorda_reward:
                reward = 1/float(self.recorda_reward[key])
        # logger.info("Recorda reward {}".format(reward))
        return reward

    def get_gui_change_reward(self):
        reward = 0
        if self.next_state and self.current_state:
            current_actions = self.current_state[1]
            next_actions = self.next_state[1]
            if len(next_actions) != 0:
                # If next state has no action, return reward 0
                shared_items = set(current_actions) & set(next_actions)
                reward = (len(next_actions) - len(shared_items))/float(len(next_actions))
        # logger.info("GUI reward {}".format(reward))
        return reward

    def get_reward(self, action):
        reward = self.get_gui_change_reward() + self.get_recorda_reward(action) + self.get_count_reward()
        return reward

    def get_random_state(self):
        return random.choice(self.visited_states.keys())[0]

    def is_out_of_app(self, activity):
        """Check is out of app."""
        if self.package in activity:
            return False
        else:
            return True

    def back_to_app(self):
        logger.info('backtoapp')
        subprocess.call(['adb', 'shell', 'monkey', '-p', self.package, '-c', 'android.intent.category.LAUNCHER', '1'])

    def jump_to_activity(self, activity):
        output = str(subprocess.check_output(['adb', 'shell', 'am', 'start', '-n', '{}/{}'.format(self.package, activity)]))
        logger.info("Jump to activity {} : {}".format(activity, output))
        return output

    def kill_app(self):
        output = str(subprocess.check_output(['adb', 'shell', 'am', 'force-stop', self.package]))
        logger.info("Kill app: {}".format(output))

    def handle_out_of_app(self, max_click):
        """
        if out of app, click maximum max_click time, then check if we're back to the app (in case of error)
        if always out of app, back to launcher
        if still out of app, restart the app
        """
        if len(self.observer.actionable_events) == 0:
            self.back_to_app()
        else:
            for i in range(max_click):
                random_action = random.choice(self.observer.actionable_events)
                self.executor.perform_action(random_action)
                if self.device.info['currentPackageName'] == self.package:
                    break

        if self.device.info['currentPackageName'] != self.package:
            self.back_to_app()

        # if self.device.info['currentPackageName'] != self.package:
        #     pid = subprocess.check_output(["adb", "shell", "ps", "|", "grep", self.package, "|", "awk", "'{ print $2 }'"])
        #     subprocess.call(["adb", "shell", "kill", str(pid)])


#force kill
# adb shell kill $(adb shell ps | grep YOUR.PACKAGE.NAME | awk '{ print $2 }')

