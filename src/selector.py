"""The event selector class."""
import random
from simplifier import Simplifier
from bisect import bisect
import kenlm


class Selector:
    """Select the event from GUI and model."""

    def __init__(self, modelpath="../output/h_PKDexActzzzzz.arpa"):
        """Initialize."""
        self.model = kenlm.Model(modelpath)
        self.simplifier = Simplifier()
        self.c_events = {}
        self.hash_events = {}

    def hash_all_gui_event(self, actionable_events):
        """Hash all gui event with md5. {hash1: event1, ....}."""
        hash_events = {}
        for e in actionable_events:
            sim = self.simplifier.simplification_gui_event(e)
            h_event = sim[0]
            hash_events[h_event] = sim[1]
        return hash_events

    def get_random_event(self, actionable_events):
        """Get a event at random regardless the probability."""
        return random.choice(actionable_events)

    def get_random_event_with_prob(self, a_events, og_events, prev_events_str):
        """Select a event regarding probability from *.arpa model.

        a_events: actionable event from Hierarchy viewer.
        og_events: 1-gram event from model.
        """
        # to be optimized.
        self.hash_events = self.hash_all_gui_event(a_events)
        back_event = self.gen_back_event()
        self.hash_events[back_event[0]] = back_event[1]
        # c = combine event
        self.c_events = self.combine_with_model(self.hash_events, og_events)
        print 'actionable len', len(self.hash_events)
        for e in self.hash_events:
            print self.hash_events[e]
        # print '1gram len', len(og_events)
        # for e in og_events:
        #     print og_events[e]
        # print 'c event len', len(self.c_events)
        # print 'intersect a and 1g', self.intersect(self.hash_events, og_events)
        score_list = []
        for e in self.hash_events:
            score = self.get_score(prev_events_str + ' ' + e)
            # biased
            if 'sc_' in e:
                print 'biasssssss'
                score *= 2.5
            elif 'back_' in e:
                score *= 2
            score_list += [(e, score)]

        # for tup in score_list:
        #     print c_events[tup[0]], tup
        # TODO: return only event that actionable on the activity.
        # print c_events

        next_event = self.weighted_choice(score_list)
        while not self.is_exist(self.hash_events, next_event):
            print '!exist, random again', next_event, self.c_events[next_event]
            next_event = self.weighted_choice(score_list)
            print 'new next_event', next_event

        return (next_event, self.c_events[next_event])

    def combine_with_model(self, actionable_events, onegram_hash_events):
        """Combine event dict from hierarchyviewer and from model.

        ideometic and accurate way from:
        http://treyhunner.com/2016/02/how-to-merge-dictionaries-in-python/
        """
        combined_events = actionable_events.copy()
        combined_events.update(onegram_hash_events)

        return combined_events

    def intersect(self, a, b):
        """Intersect."""
        return list(set(a) & set(b))

    def is_exist(self, a_events, h_event_str):
        """The event is or isn't exist in the screen."""
        if h_event_str in a_events:
            return True
        else:
            return False

    def gen_back_event(self):
        """Generate backevent."""
        back_event = {}
        back_event["eventType"] = "TYPE_BACK"
        back_event["eventText"] = 'BACK'
        back_event["resource-id"] = 'typeback'
        return ['back_', back_event]

    def get_score(self, hash_event_sequence_str):
        """Get score.

        sample input: "cl_123 cl_332 sc_881"
        return 10**log10_score (normal value)
        """
        return 10**self.model.score(hash_event_sequence_str)

    def weighted_choice(self, choices):
        """Random with weight.

        Usage: weighted_choice([("WHITE",90), ("RED",8), ("GREEN",2)]).
        """
        values, weights = zip(*choices)
        total = 0
        cum_weights = []

        for w in weights:
            total += w
            cum_weights.append(total)

        x = random.random() * total
        i = bisect(cum_weights, x)
        print 'weighted_random I:', i, choices

        return values[i]
