# -*- coding:utf-8 -*-

from swf.utils import decapitalize


EVENT_TYPES = [
    'WorkflowExecutionStarted',
    'WorkflowExecutionCompleted',
    'WorkflowExecutionFailed',
    'WorkflowExecutionTimedOut',
    'WorkflowExecutionCanceled',
    'WorkflowExecutionTerminated',
    'WorkflowExecutionContinuedAsNew',
    'WorkflowExecutionCancelRequested',
    'DecisionTaskScheduled',
    'DecisionTaskStarted',
    'DecisionTaskCompleted',
    'DecisionTaskTimedOut',
    'ActivityTaskScheduled',
    'ScheduleActivityTaskFailed',
    'ActivityTaskStarted',
    'ActivityTaskCompleted',
    'ActivityTaskFailed',
    'ActivityTaskTimedOut',
    'ActivityTaskCanceled',
    'ActivityTaskCancelRequested',
    'RequestCancelActivityTaskFailed',
    'WorkflowExecutionSignaled',
    'MarkerRecorded',
    'TimerStarted',
    'StartTimerFailed',
    'TimerFired',
    'TimerCanceled',
    'CancelTimerFailed',
    'StartChildWorkflowExecutionInitiated',
    'StartChildWorkflowExecutionFailed',
    'ChildWorkflowExecutionStarted',
    'ChildWorkflowExecutionCompleted',
    'ChildWorkflowExecutionFailed',
    'ChildWorkflowExecutionTimedOut',
    'ChildWorkflowExecutionCanceled',
    'ChildWorkflowExecutionTerminated',
    'SignalExternalWorkflowExecutionInitiated',
    'ExternalWorkflowExecutionSignaled',
    'SignalExternalWorkflowExecutionFailed',
    'RequestCancelExternalWorkflowExecutionInitiated',
    'ExternalWorkflowExecutionCancelRequested',
    'RequestCancelExternalWorkflowExecutionFailed',
]


class Event(object):
    TYPES = EVENT_TYPES
    EVENT_ATTR_SUFFIX = 'EventAttributes'

    def __init__(self, event_type,
                 event_id=-1, event_timestamp='',
                 *args, **kwargs):
        self.type = event_type
        self.id = event_id
        self.timestamp = event_timestamp

        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

    def __repr__(self):
        return '<Event %s:%s>' % (self.type, self.id)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value in Event.TYPES:
            self._type = value

    @classmethod
    def from_dict(cls, event_type,
                  event_id,
                  event_timestamp,
                  data,
                  *args, **kwargs):
        return cls(event_type, event_id, event_timestamp, **data)


class History(object):
    def __init__(self, *args, **kwargs):
        self.container = kwargs.pop('events', [])

    def __getitem__(self, val):
        if isinstance(val, int):
            return self.container[val]
        elif isinstance(val, slice):
            return self.container[val]
        else:
            raise TypeError("Unknown slice format: %s" % type(val))

    @classmethod
    def from_event_list(cls, data):
        events_history = []

        for d in data:
            event_data_key = decapitalize(d['eventType']) + 'EventAttributes'
            events_history.append(Event.from_dict(
                d['eventType'],
                d['eventId'],
                d['eventTimestamp'],
                d[event_data_key])
            )

        return cls(events=events_history)
