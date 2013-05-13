#! -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from swf.models.event.workflow import WorkflowExecutionEvent,\
                                      ChildWorkflowExecutionEvent,\
                                      ExternalWorkflowExecutionEvent
from swf.models.event.task import DecisionTaskEvent,\
                                  ActivityTaskEvent
from swf.models.event.timer import TimerEvent
from swf.models.event.marker import MarkerEvent

from swf.utils import camel_to_underscore, decapitalize


EVENTS = {
    # WorkflowExecutionEvent States : Started,
    # Completed, Failed, Signaled,
    # TimedOut, Canceled, Terminated
    # ContinuedAsNew, CancelRequested
    'WorkflowExecution': WorkflowExecutionEvent,

    # Decision Task states: Scheduled
    # Started, Completed, TimedOut
    'DecisionTask': DecisionTaskEvent,

    # Activity task states: Scheduled
    # Started, Completed, Failed,
    # TimedOut, Canceled, CancelRequested,
    # (Schedule, Failed), (RequestCancel, Failed)
    'ActivityTask': ActivityTaskEvent,

    # Marker states: Recorded
    'Marker': MarkerEvent,

    # Timer states: Started, Fired, Canceled,
    # (Start, Failed), (Cancel, Failed)
    'Timer': TimerEvent,

    # Child workflow execution states: Started,
    # Completed, Failed, TimedOut, Canceled, Terminated,
    # (Start, Initiated), (Start, Failed)
    'ChildWorkflowExecution': ChildWorkflowExecutionEvent,

    # External workflow execution states: Signaled,
    # Requested, (Signal, Initiated), (Signal, Failed)
    # (RequestCancel, Initiated), (RequestCancel, Failed)
    'ExternalWorkflow': ExternalWorkflowExecutionEvent,
}


class EventFactory(object):
    events = EVENTS

    def __new__(klass, raw_event):
        event_id = raw_event['eventId']
        event_name = raw_event['eventType']

        event_type = klass._extract_event_type(event_name)
        event_state = klass._extract_event_state(event_type, event_name)
        # amazon swf format is not very normalized and event attributes
        # response field is non-capitalized...
        event_attributes = decapitalize(event_name) + 'EventAttributes'

        klass = EventFactory.events[event_type]
        klass._name = event_name
        klass._attributes = event_attributes

        instance = klass(id=event_id, state=event_state, raw_data=raw_event)

        return instance

    @classmethod
    def _extract_event_type(klass, event_name):
        for name in klass.events.iterkeys():
            splitted = event_name.partition(name)

            if len(splitted) == 2:
                if splitted[0] == name:
                    return name
            elif len(splitted) == 3:
                if splitted[1] == name:
                    return name

        return

    @classmethod
    def _extract_event_state(klass, event_type, event_name):
        status = None
        partitioned = event_name.partition(event_type)

        if len(partitioned) == 2:
            raw_state = partitioned[1]
        elif len(partitioned) == 3:
            raw_state = ''.join(partitioned[0::2])

        klass_state = camel_to_underscore(raw_state)

        return klass_state
