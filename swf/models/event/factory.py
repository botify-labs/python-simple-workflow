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
        event_name = raw_event['eventType']
        event_type = klass._extract_event_type(event_name)
        event_state = klass._extract_event_state(event_name)

        klass = EventFactory.events[event_type]
        klass.state = event_state

        return klass

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
    def _extract_event_state(klass, event_name):
        pass
