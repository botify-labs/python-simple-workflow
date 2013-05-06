# -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from swf.models.event import EventFactory
from swf.utils import decapitalize


class History(object):
    """Simple workflow execution events history

    History object is an Event objects list container
    which can be built directly against an amazon json response
    using it's from_event_list method.

    :param  events: Events list to build History upon
    :type   events: list

    Typical amazon response looks like:

    .. code-block:: json

        {
            "events": [
                {
                    'eventId': 1,
                    'eventType': 'WorkflowExecutionStarted',
                    'workflowExecutionStartedEventAttributes': {
                        'taskList': {
                            'name': 'test'
                        },
                        'parentInitiatedEventId': 0,
                        'taskStartToCloseTimeout': '300',
                        'childPolicy': 'TERMINATE',
                        'executionStartToCloseTimeout': '6000',
                        'workflowType': {
                            'version': '0.1',
                            'name': 'test-1'
                        },
                    },
                    'eventTimestamp': 1365177769.585,
                },
                {
                    'eventId': 2,
                    'eventType': 'DecisionTaskScheduled',
                    'decisionTaskScheduledEventAttributes': {
                        'startToCloseTimeout': '300',
                        'taskList': {
                            'name': 'test'
                        }
                    },
                    'eventTimestamp': 1365177769.585
                }
            ]
        }
    """
    def __init__(self, *args, **kwargs):
        self.container = kwargs.pop('events', [])

    def __len__(self):
        return len(self.container)

    def __getitem__(self, val):
        if isinstance(val, int):
            return self.container[val]
        elif isinstance(val, slice):
            return History(events=self.container[val])

        raise TypeError("Unknown slice format: %s" % type(val))

    @property
    def last(self):
        return self.container[-1]

    def latest(self, n):
        end_pos = len(self.container)
        start_pos = len(self.container) - n
        return self.container[start_pos:end_pos]

    @property
    def first(self):
        return self.container[0]

    @classmethod
    def from_event_list(cls, data):
        """Instantiates a new Event object from dictionary

        :param  data: event history description (typically, an amazon response)
        :type   data: dict

        :returns: History model instance built upon data description
        :rtype  : swf.model.event.History
        """
        events_history = []

        for d in data:
            events_history.append(EventFactory(d))

        return cls(events=events_history)
