import itertools

import swf.models

from .event import Event


class History(swf.models.History):
    """
    Wraps the `swf.models.History` to add concepts from declarative workflows.

    """

    @property
    def last_supported_event(self):
        """
        :rtype: swf.models.event.Event

        """
        try:
            last_supported_event = (ev for ev in self.reversed if
                                    Event.is_supported(ev)).next()
        except StopIteration:  # empty result
            raise Exception('No step execution in history')
        return last_supported_event

    @property
    def last_decision(self):
        """
        :rtype: swf.models.event.Event

        """
        try:
            last_decision = (ev for ev in self.reversed if (
                             ev.type == 'DecisionTask' and
                             ev.state == 'completed')).next()
        except StopIteration:  # empty result
            raise Exception('No decision in history')
        return last_decision

    @property
    def events_since_last_decision(self):
        for event in itertools.islice(self.reversed, 1, None):
            if Event.is_supported(event):
                yield event
            elif event.type == 'DecisionTask' and event.state == 'started':
                raise StopIteration
