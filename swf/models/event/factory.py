#! -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from swf.models.event.workflow import (
    WorkflowExecutionEvent,
    CompiledWorkflowExecutionEvent,
    ChildWorkflowExecutionEvent,
    CompiledChildWorkflowExecutionEvent,
    ExternalWorkflowExecutionEvent,
    CompiledExternalWorkflowExecutionEvent
)

from swf.models.event.task import (
    DecisionTaskEvent,
    CompiledDecisionTaskEvent,
    ActivityTaskEvent,
    CompiledActivityTaskEvent
)

from swf.models.event.timer import (
    TimerEvent,
    CompiledTimerEvent
)

from swf.models.event.marker import (
    MarkerEvent,
    CompiledMarkerEvent
)

from swf.utils import camel_to_underscore, decapitalize


EVENTS = {
    'WorkflowExecution': {
        'event': WorkflowExecutionEvent,
        'compiled_event': CompiledWorkflowExecutionEvent,
    },
    'DecisionTask': {
        'event': DecisionTaskEvent,
        'compiled_event': CompiledDecisionTaskEvent,
    },
    'ActivityTask': {
        'event': ActivityTaskEvent,
        'compiled_event': CompiledActivityTaskEvent,
    },
    'Marker': {
        'event': MarkerEvent,
        'compiled': CompiledMarkerEvent,
    },
    'Timer': {
        'event': TimerEvent,
        'compiled': CompiledTimerEvent,
    },
    'ChildWorkflowExecution': {
        'event': ChildWorkflowExecutionEvent,
        'compiled': CompiledChildWorkflowExecutionEvent,
    },
    'ExternalWorkflow': {
        'event': ExternalWorkflowExecutionEvent,
        'compiled': CompiledExternalWorkflowExecutionEvent,
    },
}


class EventFactory(object):
    """Processes an input json event representation, and instantiates
    an ``swf.models.event.Event`` subclass instance accordingly.

    The input:

    .. code-block:: json

        {
            'eventId': 1,
            'eventType': 'DecisionTaskScheduled',
            'decisionTaskScheduledEventAttributes': {
                'startToCloseTimeout': '300',
                'taskList': {
                    'name': 'test'
                }
            },
            'eventTimestamp': 1365177769.585
        }

    will instantiate a ``swf.models.event.task.DecisionTaskEvent`` with state
    set to 'scheduled' from input attributes.

    :param  raw_event: The input json event representation provided by
                       amazon service
    :type   raw_event: dict

    :returns: ``swf.models.event.Event`` subclass instance
    """

    # eventType to Event subclass bindings
    events = EVENTS

    def __new__(klass, raw_event):
        event_id = raw_event['eventId']
        event_name = raw_event['eventType']
        event_timestamp = raw_event['eventTimestamp']

        event_type = klass._extract_event_type(event_name)
        event_state = klass._extract_event_state(event_type, event_name)
        # amazon swf format is not very normalized and event attributes
        # response field is non-capitalized...
        event_attributes_key = decapitalize(event_name) + 'EventAttributes'

        klass = EventFactory.events[event_type]['event']
        klass._name = event_name
        klass._attributes_key = event_attributes_key

        instance = klass(
            id=event_id,
            state=event_state,
            timestamp=event_timestamp,
            raw_data=raw_event
        )

        return instance

    @classmethod
    def _extract_event_type(klass, event_name):
        """Extracts event type from raw event_name

        :param  event_name:
        """
        for name in klass.events.iterkeys():
            splitted = event_name.partition(name)

            length = len(splitted)

            if ((length == 2 and splitted[0] == name) or
                    (length == 3 and splitted[1] == name)):
                return name

        return

    @classmethod
    def _extract_event_state(klass, event_type, event_name):
        """Extracts event state from raw event type and name"""
        partitioned = event_name.partition(event_type)

        if len(partitioned) == 2:
            raw_state = partitioned[1]
        elif len(partitioned) == 3:
            raw_state = ''.join(partitioned[0::2])

        klass_state = camel_to_underscore(raw_state)

        return klass_state


class CompiledEventFactory(object):
    events = EVENTS

    def __new__(cls, event):
        event_type = event.type

        klass = cls.events[event_type]['compiled_event']
        instance = klass(event)

        return instance
