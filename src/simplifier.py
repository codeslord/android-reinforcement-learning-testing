"""Event simplifier."""
import hashlib
import json


class Simplifier:
    """Simplify the event."""

    def simplification_event(self, event):
        """Simplify a event."""
        simplify_event = ""
        if event["eventType"] == 'TYPE_VIEW_CLICKED':
            simplify_event = self.simplify_click_event(event)
        elif event["eventType"] == 'TYPE_VIEW_SCROLLED':
            simplify_event = self.simplify_scroll_event(event)
        elif event["eventType"] == 'TYPE_VIEW_SELECTED':
            simplify_event = self.simplify_select_event(event)
        elif event["eventType"] == 'TYPE_VIEW_LONG_CLICKED':
            simplify_event = self.simplify_longclick_event(event)
        else:
            simplify_event = ['xxxxxxxxx', event["eventType"]]

        return simplify_event

    def simplify_click_event(self, clickevent):
        """Simplify a click event, return {md5: {simplify_event}}."""
        sim_event = {}
        sim_event["eventType"] = clickevent["eventType"]
        sim_event["eventText"] = clickevent["eventText"].strip("[]")

        if sim_event["eventText"] != '..':  # has eventText. dont need id.
            sim_event["resource-id"] = "noneId"
        else:
            if "resource-id" in clickevent:
                sim_event["resource-id"] = clickevent["resource-id"]
            else:
                sim_event["resource-id"] = "noneId"

        hash_e = "cl_" + self.hash_event(json.dumps(sim_event))

        return [hash_e, sim_event]

    def simplify_longclick_event(self, clickevent):
        """Simplify a click event, return {md5: {simplify_event}}."""
        sim_event = {}
        sim_event["eventType"] = clickevent["eventType"]
        sim_event["eventText"] = clickevent["eventText"].strip("[]")

        if sim_event["eventText"] != '..':  # has eventText. dont need id.
            sim_event["resource-id"] = "noneId"
        else:
            if "resource-id" in clickevent:
                sim_event["resource-id"] = clickevent["resource-id"]
            else:
                sim_event["resource-id"] = "noneId"

        hash_e = "lcl_" + self.hash_event(json.dumps(sim_event))

        return [hash_e, sim_event]

    def simplify_scroll_event(self, scrollevent):
        """Simplify a scroll event, return {md5: {simplify_event}}."""
        sim_event = {}
        sim_event["eventType"] = scrollevent["eventType"]
        sim_event["eventText"] = scrollevent["eventText"].strip("[]")

        # if "fromY" in scrollevent:
        #     sim_event["fromY"] = scrollevent["fromY"]
        #     sim_event["toY"] = scrollevent["toY"]
        # else:
        #     sim_event["fromIndex"] = scrollevent["fromIndex"]
        #     sim_event["toIndex"] = scrollevent["toIndex"]

        if len(sim_event["eventText"]) != '..':  # has eventText. dont need id.
            sim_event["resource-id"] = "noneId"
        else:
            if "resource-id" in scrollevent:
                sim_event["resource-id"] = scrollevent["resource-id"]
            else:
                sim_event["resource-id"] = "noneId"

        hash_e = "sc_" + self.hash_event(json.dumps(sim_event))
        return [hash_e, sim_event]

    def simplify_select_event(self, selectevent):
        """Simplify a select event, return {md5: {simplify_event}}."""
        sim_event = selectevent
        hash_e = "se_" + self.hash_event(json.dumps(sim_event))
        return [hash_e, sim_event]

    def hash_event(self, raw_event):
        """Create md5 hash of the event dict."""
        return hashlib.md5(str(raw_event)).hexdigest()

    # GUI EVENT

    def simplification_gui_event(self, event):
        """Simplify a gui event."""
        simplify_event = ""

        # DEBUG
        if (event.attrib["clickable"] == 'true' and
           event.attrib["scrollable"] == 'true'):
                print '------------------'
                print '2 possible actions', event.attrib
        # END

        if event.attrib["clickable"] == 'true':
            simplify_event = self.simplify_gui_click_event(event)
        elif event.attrib["scrollable"] == 'true':
            simplify_event = self.simplify_gui_scroll_event(event)
        elif event.attrib["long-clickable"] == 'true':
            simplify_event = self.simplify_gui_longclick_event(event)
        # elif event.attrib["eventType"] == 'TYPE_VIEW_SELECTED':
            # simplify_event = self.simplify_gui_select_event(event)
        else:
            simplify_event = ['xxxxxxxxx', event.attrib["clickable"]]

        return simplify_event

    def simplify_gui_click_event(self, guievent):
        """Simplify an event that aqquired from hierarchy dump."""
        sim_gui_event = {}
        sim_gui_event["eventType"] = "TYPE_VIEW_CLICKED"
        sim_gui_event["eventText"] = guievent.attrib["text"]

        if len(sim_gui_event["eventText"]) != '..':  # has eventText. dont need id.
            sim_gui_event["resource-id"] = "noneId"
        else:
            if ("resource-id" in guievent.attrib and
               guievent.attrib["resource-id"] != ''):
                sim_gui_event["resource-id"] = guievent.attrib["resource-id"]
            else:
                sim_gui_event["resource-id"] = "noneId"

        hash_e = "cl_" + self.hash_event(json.dumps(sim_gui_event))

        return [hash_e, sim_gui_event]

    def simplify_gui_longclick_event(self, guievent):
        """Simplify an event that aqquired from hierarchy dump."""
        sim_gui_event = {}
        sim_gui_event["eventType"] = "TYPE_VIEW_LONG_CLICKED"
        sim_gui_event["eventText"] = guievent.attrib["text"]

        if len(sim_gui_event["eventText"]) != '..':  # has eventText. dont need id.
            sim_gui_event["resource-id"] = "noneId"
        else:
            if ("resource-id" in guievent.attrib and
               guievent.attrib["resource-id"] != ''):
                sim_gui_event["resource-id"] = guievent.attrib["resource-id"]
            else:
                sim_gui_event["resource-id"] = "noneId"

        hash_e = "lcl_" + self.hash_event(json.dumps(sim_gui_event))

        return [hash_e, sim_gui_event]

    def simplify_gui_scroll_event(self, guievent):
        """Simplify an event that aqquired from hierarchy dump."""
        # WIP
        sim_gui_event = {}
        sim_gui_event["eventType"] = "TYPE_VIEW_SCROLLED"
        sim_gui_event["eventText"] = guievent.attrib["text"]

        # if "fromY" in guievent:
        #     sim_gui_event["fromY"] = guievent["fromY"]
        #     sim_gui_event["toY"] = guievent["toY"]
        # else:
        #     sim_gui_event["fromIndex"] = guievent["fromIndex"]
        #     sim_event["toIndex"] = guievent["toIndex"]

        if len(sim_gui_event["eventText"]) != '..':  # has eventText. dont need id.
            sim_gui_event["resource-id"] = "noneId"
        else:
            if ("resource-id" in guievent.attrib and
               guievent.attrib["resource-id"] != ''):
                sim_gui_event["resource-id"] = guievent.attrib["resource-id"]
            else:
                sim_gui_event["resource-id"] = "noneId"
        hash_e = "sc_" + self.hash_event(json.dumps(sim_gui_event))

        return [hash_e, sim_gui_event]

    def simplify_gui_select_event(self, guievent):
        """Simplify a select event that aqquired from hierarchy dump."""
        sim_gui_event = guievent
        hash_e = "se_" + self.hash_event(json.dumps(sim_gui_event))
        return [hash_e, sim_gui_event]
