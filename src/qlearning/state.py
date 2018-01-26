from simplifier import Simplifier
import operator
import uuid
DEFAULT_Q = 0
import pprint

pp = pprint.PrettyPrinter(indent=4)


class State(object):
    id = None
    activity = ""
    hash_actions = {}  # hash_action: [simplified action, gui action]
    q_value = {}

    def __init__(self, activity_name, clickable_components):
        self.id = uuid.uuid4()
        self.activity = activity_name
        self.hash_actions = hash_all_gui_event(clickable_components)
        self.q_value = {}
        for c in self.hash_actions:
            self.q_value[get_state_hash_action_key(self, c)] = DEFAULT_Q

    def update_q(self, hash_action, value):
        key = get_state_hash_action_key(self, hash_action)
        if key in self.q_value:
            self.q_value[key] = value

    def __str__(self):
        action_str = ""
        action_sim = map(operator.itemgetter(0), self.hash_actions.values())
        for a in action_sim:
            action_str += str(a)
        return "{} - {} actions: {}".format(self.activity, len(self.hash_actions), action_str)


def get_state_hash_action_key(state, hash_action):
    return "{}||{}".format(state.activity, hash_action).encode('utf-8').strip()


def get_state_action_key(state, component):
    simplifier = Simplifier()
    hash_action = simplifier.simplification_gui_event(component)[0]
    return "{}||{}".format(state.activity, hash_action).encode('utf-8').strip()


def hash_all_gui_event(actionable_events):
    """Hash all gui event with md5. {hash1: event1, ....}."""
    hash_events = {}
    for e in actionable_events:
        simplifier = Simplifier()
        sim = simplifier.simplification_gui_event(e)
        h_event = sim[0]
        hash_events[h_event] = [sim[1], sim[2]]
    return hash_events


def compare_action(self, gui_action, recorda_action):
    # gui_action from hierachy dump
    # recorda action from recorda output json file
    s = Simplifier()
    gui_action_sim = s.simplification_gui_event(gui_action).values()[0][0]
    return (gui_action_sim['eventType'] == recorda_action['eventType'] and gui_action_sim['eventText'] == recorda_action[
        'eventText'] and gui_action_sim['resource-id'] == 'noneId') or (
        gui_action_sim['resource-id'] != 'noneId' and 'resource-id' in recorda_action and gui_action_sim['resource-id'] == recorda_action['resource-id'])


def equal_actions(clickable_actions1, clickable_actions2):
    hash1 = hash_all_gui_event(clickable_actions1)
    hash2 = hash_all_gui_event(clickable_actions2)
    if len(hash1) != len(hash2):
        return False
    paired = zip(map(operator.itemgetter(0), hash1.values()), map(operator.itemgetter(0), hash2.values()))
    shared_items = [(x, y) for (x, y) in paired if x == y]
    if len(shared_items) != len(hash1):
        return False
    return True


def equal_hash_actions(hash1, hash2):
    if len(hash1) != len(hash2):
        return False
    paired = zip(map(operator.itemgetter(0), hash1.values()), map(operator.itemgetter(0), hash2.values()))
    shared_items = [(x, y) for (x, y) in paired if x == y]
    if len(shared_items) != len(hash1):
        return False
    return True
