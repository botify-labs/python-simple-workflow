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

    def __init__(self, id=None, state=None, last_event_id=None,
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
        self._id = id
        self._state = state

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
