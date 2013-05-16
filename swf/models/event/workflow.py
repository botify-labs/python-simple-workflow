#! -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from swf.models.event.base import Event
from swf.models.event.compiler import CompiledEvent


class WorkflowExecutionEvent(Event):
    _type = 'WorkflowExecution'


class CompiledWorkflowExecutionEvent(CompiledEvent):
    _type = 'WorkflowExecution'
    states = (
        'started',
        'completed',
        'failed',
    )

    transitions = {
        'started': ('failed', 'completed')
    }

    initial_state = 'started'


class ChildWorkflowExecutionEvent(Event):
    _type = 'ChildWorkflowExecution'


class CompiledChildWorkflowExecutionEvent(CompiledEvent):
    _type = 'ChildWorkflowExecution'

    states = (
        'start_initiated',
        'start_failed',
        'started',
        'completed',
        'failed',
        'timed_out',
        'canceled',
        'terminated',
    )

    transitions = {
        'start_initiated': ('start_failed', 'started'),
        'start_failed': ('failed'),
        'started': ('canceled', 'failed', 'timed_out', 'terminated'),
    }

    initial_state = 'start_initiated'


class ExternalWorkflowExecutionEvent(Event):
    _type = 'ExternalWorkflowExecution'


class CompiledExternalWorkflowExecutionEvent(CompiledEvent):
    _type = 'ExternalWorkflowExecution'

    states = (
        'signal_initiated',
        'signaled',
        'signal_failed',
        'request_cancel_initiated',
        'cancel_requested',
        'request_cancel_failed',
    )

    transitions = {
        'signal_initiated': ('signal_failed', 'signaled'),
        'request_cancel_initiated': ('request_cancel_failed'),
        'cancel_requested': ('request_cancel_failed'),
    }

    initial_state = 'signal_initiated'
