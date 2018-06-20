import hashlib
import operator

from src.env.recorda.simplifier import Simplifier

DEFAULT_Q = 0
import pprint

pp = pprint.PrettyPrinter(indent=4)


class State(object):
    id = None
    activity = ""
    hash_actions = {}  # hash_action: [simplified action, gui action]
    q_value = {}

    def __init__(self, activity_name, clickable_components):
        self.activity = activity_name
        self.hash_actions = hash_all_gui_event(clickable_components)
        self.q_value = {}
        for c in self.hash_actions:
            self.q_value[get_qvalue_key(self, c)] = DEFAULT_Q
        hash_object = {
            "activity": self.activity,
            "actions": self.hash_actions.keys()
        }
        self.id = hashlib.md5(str(hash_object)).hexdigest()

    def update_q(self, hash_action, value):
        key = get_qvalue_key(self, hash_action)
        if key in self.q_value:
            self.q_value[key] = value

    def __str__(self):
        action_str = ""
        action_sim = map(operator.itemgetter(0), self.hash_actions.values())
        for a in action_sim:
            action_str += str(a)
        return "{} - {} actions: {}".format(self.activity, len(self.hash_actions), action_str)


def get_qvalue_key(state, hash_action):
    return "{}||{}".format(state.activity, hash_action).encode('utf-8').strip()


def get_state_action_key(state, component):
    simplifier = Simplifier()
    hash_action = simplifier.simplification_gui_event(component)[0]
    return "{}||{}".format(state.activity, hash_action).encode('utf-8').strip()


def hash_all_gui_event(actionable_events):
    """Hash all gui event with md5. {hash1: event1, ....}."""
    hash_events = {}
    for e in actionable_events:
        if ('com.android.systemui:id/' not in e.attrib["resource-id"] and 'com.google.android.googlequicksearchbox' not in e.attrib["resource-id"]) or e.attrib["resource-id"] == 'com.android.systemui:id/back':
            simplifier = Simplifier()
            sim = simplifier.simplification_gui_event(e)
            h_event = sim[0]
            hash_events[h_event] = [sim[1], sim[2]]
    return hash_events
