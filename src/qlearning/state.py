from simplifier import Simplifier

DEFAULT_Q = 0.5

class State(object):
    activity = ""
    actions = []
    hash_actions = {}
    q_value = {}

    def __init__(self, activity_name, clickable_components):
        self.activity = activity_name
        self.actions = clickable_components
        for c in self.actions:
            self.q_value[get_state_action_key(self, c)] = DEFAULT_Q
        self.hash_actions = hash_all_gui_event(clickable_components)

    def update_q(self, hash_action, value):
        key = get_state_hash_action_key(self, hash_action)
        self.q_value[key] = value


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
