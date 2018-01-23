import xmltodict

class State(object):
    activity = ""
    actions = None
    q_value = {}

    def __init__(self, activity_name, clickable_components):
        self.activity = activity_name
        print(self.activity)
        self.actions = clickable_components
        for c in self.actions:
            self.q_value[get_state_component_key(self, c)] = 0.5
            print("setting q value for {} = 0.5".format(get_state_component_key(self, c)))


def get_state_component_key(state, component):
    return "{}:{}|{}|{}".format(state.activity, component.attrib["resource-id"], component.attrib["class"], component.attrib["text"])