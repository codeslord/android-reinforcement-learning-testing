"""WIP."""
from xml.etree import cElementTree as ET
from uiautomator import Device
from subprocess import check_output
import copy


class GuiObserver:
    """Gui guiobserver.py."""

    def __init__(self, device=Device('60e701c935a2')):
        """Initialize with android automator's device."""
        if type(device) is Device:
            self.device = device
        else:
            print 'ERROR: please input automator.Device as param.'

    def dump_gui(self, path):
        """Dump gui hierarchy from device and save as *.xml format."""
        dd = self.device.dump().encode('utf-8')
        tree = ET.ElementTree(ET.fromstring(dd))
        self.passing_actionable_to_children(tree.getroot(),
                                            False, False, False)
        tree.write(path)
        # self.device.dump(path)

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

    # def get_all_clickable_events(self, tree):
    #     """Get all clickable events from given xml tree."""
    #     allclickable = tree.findall(".//*[@clickable='true']")
    #
    #     return allclickable

    def get_actionable_events(self, event_type, tree):
        """Get all given event_type event."""
        rexstr = ".//*[@" + event_type + "='true']"
        all_given_events = tree.findall(rexstr)
        return all_given_events

    def get_all_actionable_events(self, hierarchy_path):
        """Get all actionable events from given hierarchy.xml path."""
        tree = self.get_tree_from_dump(hierarchy_path)
        event_types = ["clickable",
                       "long-clickable",
                       #    "focusable",
                       "checkable",
                       "scrollable"]

        all_actionable_events = []

        for e in event_types:
            all_actionable_events += self.get_actionable_events(e, tree)

        dup_actionable_events = []
        for e in all_actionable_events:
            dup_actionable_events += self.dup_event(e)

        return dup_actionable_events

    # def gen_back_event(self):
    #     """WIP: Generate click 'back button' on android device event."""

    def get_tree_from_dump(self, hierarchyPath):
        """Get tree from dump hierarchy path."""
        tree = ET.parse(hierarchyPath)
        return tree

    def find_gui_from_event(self, hierarchyPath, event):
        """Find and return GUI component given an event.

        return Element from ElementTree.
        """
        tree = self.get_tree_from_dump(hierarchyPath)
        print 'findguifromevent: ', event
        if event['resource-id'] == 'typeback':
            return
        if event['resource-id'] == 'noneId':
            resid = ""
        else:
            resid = event['resource-id']
        txt = event['eventText']
        print 'gui_from_event>>>>>>>>>>>>>>>>>', event
        # rexstr = ".//*[@" + 'resource-id' + "='" + resid + "']"
        rexstr = ".//*[@" + 'text' + "='" + txt + "']"
        all_given_events = tree.findall(rexstr)
        if len(all_given_events) == 0:
            # rexstr = ".//*[@" + 'text' + "='" + txt + "']"
            rexstr = ".//*[@" + 'resource-id' + "='" + resid + "']"
            all_given_events += tree.findall(rexstr)
        elif len(all_given_events) > 1:
            # rexstr = ".//*[@" + 'text' + "='" + txt + "']"
            rexstr = ".//*[@" + 'resource-id' + "='" + resid + "']"
            all_given_events = list(set(all_given_events) -
                                    set(tree.findall(rexstr)))
        # else 1.... ok

        if len(all_given_events) == 0:
            print('SOMETHING WENT WRONG WITH', event)
        elif len(all_given_events) == 1:
            return all_given_events[0]
        else:  # debug
            if len(all_given_events) > 1:
                print 'OMG MORE THAN ONE--------------------------'
                print all_given_events
                return all_given_events[0]

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
