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
    """Simple workflow execution event wrapper

    :param      event_type: type of event represented
    :type       event_type: String
    """
    TYPES = EVENT_TYPES
    EVENT_ATTR_SUFFIX = 'EventAttributes'

    def __init__(self, event_type,
                 event_id=-1, event_timestamp='',
                 *args, **kwargs):
        self._type = None

        self.id = event_id
        self.timestamp = event_timestamp
        self.type = event_type

        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

    def __repr__(self):
        return '<Event %s:%s>' % (self.type, self.id)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value not in Event.TYPES:
            raise ValueError("Invalid type supplied: %s" % self.type)
        self._type = value

    @classmethod
    def from_dict(cls, event_type,
                  event_id,
                  event_timestamp,
                  data,
                  *args, **kwargs):
        return cls(event_type, event_id, event_timestamp, **data)


class History(object):
    """Simple workflow execution events history

    History object is an Event objects list container
    which can be built directly against an amazon json response
    using it's from_event_list method.

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

    def __getitem__(self, val):
        if isinstance(val, int):
            return self.container[val]
        elif isinstance(val, slice):
            return History(events=self.container[val])
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
