#! -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from datetime import datetime

from swf.models.event.states import EventState
from swf.utils import Enum, camel_to_underscore, cached_property


EVENT_TYPE = Enum(
    'ACTIVITY',
    'DECISION',
    'CHILD_WORKFLOW',
    'WORKFLOW',
    'SIGNAL_RECEIVED',
    'SIGNAL_SENT',
    'TIMER_RECEIVED',
    'TIMER_SET',
    'WORKFLOW_SIGNALED',
    'NOT_IMPLEMENTED',
)


class Event(object):
    """Simple workflow execution event wrapper
    """
    _type = None
    _name = None
    _attributes_key = None
    _attributes = None

    excluded_attributes = (
        'eventId',
        'eventType',
        'eventTimestamp'
    )

    def __init__(self, id, state, timestamp, raw_data):
        """
        """
        self._id = id
        self._state = state
        self._timestamp = timestamp
        self.raw = raw_data or {}

        self.process_attributes()

    def __repr__(self):
        return '<Event %s %s : %s >' % (self.id, self.type, self.state)

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @cached_property
    def timestamp(self):
        return datetime.fromtimestamp(self._timestamp)

    def process_attributes(self):
        for key, value in self.raw[self._attributes_key].iteritems():
            setattr(self, camel_to_underscore(key), value)
