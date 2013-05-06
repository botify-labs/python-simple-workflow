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
    _state = None

    def __init__(self, last_event_id=None,
                 control=None, worker_id=None,
                 task_list=None, execution=None,
                 execution_context=None, dt_decided=None,
                 dt_started=None, dt_last_event=None,
                 last_history_event=None,
                 event_history_incomplete=None,
                 cause=None, cause_details=None,
                 **kwargs):
        """
        """
        self.last_event_id = last_event_id
        self.control = control
        self.worker_id = worker_id
        self.task_list = task_list
        self.execution = execution
        self.execution_context = execution_context
        self.dt_decided = dt_decided
        self.dt_started = dt_started
        self.dt_last_event = dt_last_event
        self.last_history_event = last_history_event
        self.event_history_incomplete = event_history_incomplete
        self.cause = cause
        self.cause_details = cause_details

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        return '<Event %s:%s>' % (self._type, self.id)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        """Sets event type ensuring provided value is
        part of swf.models.event.EVENT_TYPES

        :param  value: Supplied type to set
        :type   type: swf.models.event.EVENT_TYPES member
        """
        if not EVENT_TYPE.has_member(value):
            raise ValueError("Unknown provided event type")
        self._type = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        """Sets event name ensuring provided value is
        member of swf.models.event.EVENT_NAMES

        :param  value: Supplied name to set
        :type   value: swf.models.event.EVENT_NAMES member
        """
        if not EVENT_NAMES.has_member(value):
            raise ValueError("Unknown provided event name")
        self._name = value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        """Sets event state ensuring provided value is
        instance of swf.models.event.EventState type

        :param  value: Supplied state to set
        :type   value: swf.models.event.EventState
        """
        if not isinstance(value, EventState):
            raise TypeError("Event state has to be an instance of EventState")
        self._state = value
