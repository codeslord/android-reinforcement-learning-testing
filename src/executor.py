"""The main function and Executor class."""
from xml.etree import cElementTree as ElementTree
import re
import random
from uiautomator import Device
import subprocess
from random import randint

class Executor:
    """Execute the Events."""

    def __init__(self, device=Device('60e701c935a2')):
        """Initialize."""
        self.device = device

    def get_center_from_bound(self, boundStr):
        """Get center from bound."""
        bound = re.findall(r'\d+', boundStr)
        x1 = int(bound[0])
        y1 = int(bound[1])
        x2 = int(bound[2])
        y2 = int(bound[3])
        return [(x1+x2)/2, (y1+y2)/2]

    def get_random_point_from_bound(self, boundStr):
        """Get random x,y points from bound."""
        bound = re.findall(r'\d+', boundStr)
        x1 = int(bound[0])
        y1 = int(bound[1])
        x2 = int(bound[2])
        y2 = int(bound[3])
        xa = random.randint(x1, x2)
        ya = random.randint(y1, y2)
        return [xa, ya]

    def perform_scroll(self, event):
        """Perform scroll from x1y1 to x2y2 randomly."""
        bound_str = event.attrib['bounds']
        x1, y1 = self.get_random_point_from_bound(bound_str)
        x2, y2 = self.get_random_point_from_bound(bound_str)
        self.device.drag(x1, y1, x2, y2, steps=30)
        print 'scroll:', event.attrib['resource-id']
        print 'from:', x1, y1, 'to:', x2, y2
        return True

    def perform_click(self, event):
        """Perform click at x,y from eventbound."""
        x, y = self.get_center_from_bound(event.attrib['bounds'])
        self.device.click(x, y)
        print 'click:', event.attrib['text']
        print 'at', x, y
        return True

    def perform_random_click(self, x, y):
        """Perform random click at x,y."""
        # print 'randomclick:'
        # print 'at', x, y
        self.device.click(x, y)
        return True

    def perform_click_and_text(self, event):
        """Perform click and Text."""
        self.perform_click(event)
        self.adb_text(self.gen_random_text())

    def gen_random_text(self):
        """Gen random text."""
        le = (randint(1, 16))
        choice = (randint(0, 10))
        arr = []
        if choice == 0 or choice == 4 or choice == 5:
            arr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        elif choice == 1:
            arr = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        elif choice == 2:
            arr = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
        elif choice == 3:
            arr = list('(*&^%$#@!{abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
        elif choice == 6:
            return 'DEL'
        else:
            return ''
        return ''.join(random.choice(arr) for x in range(le))

    def adb_del_text(self, count):
        """ADB del."""
        subprocess.call(
                ['adb', 'shell', 'input', 'keyevent', 'KEYCODE_MOVE_END'])
        for i in range(count):
            subprocess.call(
                ['adb', 'shell', 'input', 'keyevent', 'KEYCODE_DEL'])

    def adb_text(self, text):
        """Fire a text event."""
        if len(text) == 0:
            return
        elif text == 'DEL':
            self.adb_del_text(randint(1, 20))
        else:
            subprocess.call(['adb', 'shell', 'input', 'keyboard', 'text',
                            '"'+text+'"'])
            subprocess.call(['adb', 'shell', 'input', 'keyevent', '111'])

    def perform_longclick(self, event):
        """Perform click at x,y from eventbound."""
        x, y = self.get_center_from_bound(event.attrib['bounds'])
        self.device.long_click(x, y)
        print 'longclick:', event.attrib['text']
        print 'at', x, y
        return True

    # TODO: support multiple action.
    def perform_action_with_hash(self, event, h_event):
        """Perform an action base on event type."""
        if h_event["eventType"] == 'TYPE_VIEW_CLICKED':
            if 'Text' in event.attrib["class"]:
                # print '------contain text-------'
                return self.perform_click_and_text(event)
            return self.perform_click(event)
        elif h_event["eventType"] == 'TYPE_VIEW_SCROLLED':
            return self.perform_scroll(event)
        elif h_event["eventType"] == 'TYPE_VIEW_LONG_CLICKED':
            return self.perform_longclick(event)
        else:
            print 'non clickable or scrollable action. >>>skip', event
            return False

    def perform_action(self, event):
        """Perform an action base on event type."""
        if event.attrib["clickable"] == 'true':
            if 'Text' in event.attrib["class"]:
                # print '------contain text-------'
                return self.perform_click_and_text(event)
            return self.perform_click(event)
        elif event.attrib["scrollable"] == 'true':
            return self.perform_scroll(event)
        elif event.attrib["long-clickable"] == 'true':
            return self.perform_longclick(event)
        else:
            print 'non clickable or scrollable action. >>>skip', event
            return False

    def perform_action_from_simplified_event(self, event):
        """Perform action from simplified event."""
        if event["eventType"] == 'TYPE_VIEW_CLICKED':
            self.perform_click(event)
        elif event["eventType"] == 'TYPE_VIEW_SCROLLED':
            self.perform_scroll(event)
        elif event["eventType"] == 'TYPE_VIEW_LONG_CLICKED':
            self.perform_longclick(event)
        elif event["eventType"] == 'back':
            self.perform_back()
        else:
            print 'non clickable or scrollable action. >>>skip', event

    def perform_back(self):
        """Press back button on device."""
        self.device.press.back()
