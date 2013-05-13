#! -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from swf.models.event.states import EventState
from swf.utils import Enum


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
    _attributes = None

    def __init__(self, id, state, raw_data):
        """
        """
        self._id = id
        self._state = state
        self.raw = raw_data or {}

        self.last_event_id = None
        self.control = None
        self.identity = None
        self.task_list = None
        self.execution = None
        self.execution_context = None
        self.dt_decided = None
        self.dt_started = None
        self.dt_last_event = None
        self.last_history_event = None
        self.event_history_incomplete = None
        self.cause = None
        self.cause_details = None

        # Call for automatic attributes set
        # from data using the from_data method.
        # should be implemented in child classes
        self.from_data(raw_data)

    def __repr__(self):
        return '<Event %s %s : %s >' % (self.id, self.type, self.state)

    def from_data(self, data):
        raise NotImplementedError

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
