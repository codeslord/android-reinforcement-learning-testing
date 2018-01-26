"""WIP."""
from xml.etree import cElementTree as ET
from uiautomator import Device
from subprocess import check_output
import copy


class GuiObserver:
    """Gui guiobserver.py."""

    def __init__(self, device=Device('60e701c935a2')):
        """Initialize with android automator's device."""
        self.tree = None
        if type(device) is Device:
            self.device = device
        else:
            print 'ERROR: please input automator.Device as param.'

    def dump_gui(self):
        """Dump gui hierarchy from device."""
        self.tree = None
        dd = self.device.dump().encode('utf-8')
        tree = ET.ElementTree(ET.fromstring(dd))
        self.passing_actionable_to_children(tree.getroot(),
                                            False, False, False)
        self.tree = tree

    def dup_event(self, actionable_event):
        """Clickable+scrollable = clickable, scrollable."""
        res = []
        if actionable_event.get('clickable') == 'true':
            dup = copy.deepcopy(actionable_event)
            dup.set('clickable', 'true')
            dup.set('scrollable', 'false')
            dup.set('long-clickable', 'false')
            res += [dup]
        if actionable_event.get('scrollable') == 'true':
            dup = copy.deepcopy(actionable_event)
            dup.set('clickable', 'false')
            dup.set('scrollable', 'true')
            dup.set('long-clickable', 'false')
            res += [dup]
        if actionable_event.get('long-clickable') == 'true':
            dup = copy.deepcopy(actionable_event)
            dup.set('clickable', 'false')
            dup.set('scrollable', 'false')
            dup.set('long-clickable', 'true')
            res += [dup]
        return res

    def get_actionable_events(self, event_type, tree):
        """Get all given event_type event."""
        rexstr = ".//*[@" + event_type + "='true']"
        all_given_events = tree.findall(rexstr)
        return all_given_events

    def get_all_actionable_events(self):
        """Get all actionable events from given hierarchy.xml path."""
        event_types = ["clickable",
                       "long-clickable",
                       #    "focusable",
                       "checkable",
                       "scrollable"]

        all_actionable_events = []

        for e in event_types:
            all_actionable_events += self.get_actionable_events(e, self.tree)

        dup_actionable_events = []
        for e in all_actionable_events:
            dup_actionable_events += self.dup_event(e)

        return dup_actionable_events

    def get_current_activity(self, current_package):
        """Get current activity of current package."""
        # $adb shell dumpsys window windows | grep -E 'mCurrentFocus'
        # mCurrentFocus=Window{a55fe368 u0 com.octtoplus.proj.recorda/
        # com.octtoplus.proj.recorda.MainActivity}
        # return MainActivity
        output = check_output(['adb', 'shell', 'dumpsys', 'window',
                               'windows', '|', 'grep', '-E',
                               "'mCurrentFocus'"])
        cur_activity = output.split('/')[-1].replace(current_package+'.', '').split('}')[0]
        return cur_activity

    def passing_actionable_to_children(self, root, clickable, scrollable, longclickable):
        """Passing actionable to children node."""
        if len(root.getchildren()) == 0:
            return
        else:
            for node in root:
                actionable = node.get('clickable')
                s_actionable = node.get('scrollable')
                l_actionable = node.get('long-clickable')
                if (self.encode_bool(actionable) or clickable):
                    node.set('clickable', 'true')
                else:
                    node.set('clickable', 'false')

                if (self.encode_bool(s_actionable) or scrollable):
                    node.set('scrollable', 'true')
                else:
                    node.set('scrollable', 'false')

                if (self.encode_bool(l_actionable) or longclickable):
                    node.set('long-clickable', 'true')
                else:
                    node.set('long-clickable', 'false')
                actionable = node.get('clickable')
                s_actionable = node.get('scrollable')
                l_actionable = node.get('long-clickable')
                self.passing_actionable_to_children(
                    node, self.encode_bool(actionable),
                    self.encode_bool(s_actionable),
                    self.encode_bool(l_actionable))

    def encode_bool(self, boolstr):
        """Encode 'true' to True."""
        if boolstr == 'true':
            return True
        else:
            return False
