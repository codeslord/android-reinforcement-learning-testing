"""Model builder class."""
from subprocess import call

from qlearning.simplifier import Simplifier
from utils import *


class ModelBuilder:
    """Model builder class using KenLM."""

    def __init__(self, raw_events):
        """Initialize the class."""
        self.raw_events = raw_events  # event from Recorda
        # self.h_events, self.h_events_str = self.create_hash_events(raw_events)
        self.h_event_count, self.h_event_freq = self.create_hash_events_with_frequency(raw_events)

    def trim_newline(self, text):
        """Remove empty newline or trailing space."""
        return "".join([s for s
                        in text.strip().splitlines(True)
                        if s.strip()])

    def create_hash_events(self, raw_events):
        """Hash all the events in dict and seq of hash events.

        format of dict: [{hashValue1: event1}, ...]
        """
        hash_events = {}
        hash_events_str = ''
        simplifier = Simplifier()
        for e in raw_events:
            if e["eventType"] == 'TYPE_WINDOW_STATE_CHANGED':
                h_event = simplifier.hash_event(e)
                hash_events_str += '\n'
            else:
                sim = simplifier.simplification_event(e)
                h_event = sim[0]
                hash_events[h_event] = sim[1]
                hash_events_str += sim[0] + ' '

        hash_events_str = self.trim_newline(hash_events_str)
        # hash_events_str = ' '.join(hash_events_list)
        return [hash_events, hash_events_str]

    def create_hash_events_with_frequency(self, raw_events):
        """Hash all the events in dict and seq of hash events.

        format of dict: {hashValue1: simplified event1, hashValue2: simplified event2}, ...
        """
        hash_events = {}
        hash_events_count = {}
        simplifier = Simplifier()
        for e in raw_events:
            if e["eventType"] == 'TYPE_WINDOW_STATE_CHANGED':
                h_event = simplifier.hash_event(e)
            else:
                sim = simplifier.simplification_event(e)
                h_event = sim[0]
                hash_events[h_event] = sim[1]
                if h_event in hash_events_count:
                    hash_events_count[h_event] += 1
                else:
                    hash_events_count[h_event] = 1
        hash_freq = {k: v/float(len(raw_events)) for k, v in hash_events_count.items()}
        return hash_events_count, hash_freq

    def save_hash_events(self, eventstr, filename):
        """Hash all event to a file."""
        path = '../output/'+filename
        write_string_to_file(eventstr, path)

    def create_klm_model_from_events(self, events, filename):
        """Parse events to .klm file.

        create hash events then save to disk.
        then call cmd to create .arpa
        """
        self.h_events, self.h_events_str = self.create_hash_events(events)
        self.save_hash_events(self.h_events_str, filename)

        call(['../kenlm/bin/lmplz', '-o', '3', '--discount_fallback'],
             stdin=open('../output/'+filename, 'r'),
             stdout=open('../output/'+filename+'.arpa', 'w'))

    def get_score(self, event_seq):
        """Get probability of the event sequence."""
        return self.model.score(event_seq)
