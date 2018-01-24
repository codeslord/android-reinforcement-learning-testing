DEFAULT_Q = 0.5

class State(object):
    activity = ""
    actions = None
    q_value = {}

    def __init__(self, activity_name, clickable_components):
        self.activity = activity_name
        print(self.activity)
        self.actions = clickable_components
        for c in self.actions:
            self.q_value[get_state_component_key(self, c)] = DEFAULT_Q

    def update_q(self, action, value):
        key = get_state_component_key(self, action)
        self.q_value[key] = value


def get_state_component_key(state, component):
    return "{}||{}|{}|{}".format(state.activity, component.attrib["resource-id"].encode('utf-8'), component.attrib["class"].encode('utf-8'), component.attrib["text"].encode('utf-8')).strip()