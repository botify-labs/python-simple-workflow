#! -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from swf.models.event.base import Event
from swf.models.event.compiler import CompiledEvent


class ActivityTaskEvent(Event):
    _type = 'ActivityTask'


class CompiledActivityTaskEvent(CompiledEvent):
    _type = 'ActivityTask'
    states = (
        'scheduled',
        'schedule_failed',
        'started',
        'completed',
        'failed',
        'timed_out',
        'canceled',
        'cancel_requested',
        'request_cancel_failed',
    )

    transitions = {
        'scheduled': ('schedule_failed', 'canceled', 'timed_out', 'started'),
        'schedule_failed': ('scheduled', 'timed_out'),
        'started': ('canceled', 'failed', 'timed_out', 'completed'),
        'failed': ('scheduled', 'timed_out'),
        'timed_out': ('scheduled'),
        'canceled': ('scheduled', 'timed_out'),
        'cancel_requested': ('canceled', 'request_cancel_failed', 'timed_out'),
        'request_cancel_failed': ('scheduled', 'timed_out'),
    }

    initial_state = 'scheduled'

class DecisionTaskEvent(Event):
    _type = 'DecisionTask'


class CompiledDecisionTaskEvent(CompiledEvent):
    _type = 'DecisionTask'
    states = (
        'scheduled',
        'started',
        'completed',
        'timed_out'
    )

    transitions = {
        'scheduled': ('started'),
        'started': ('timed_out', 'completed'),
        'timed_out': ('scheduled'),
    }

    initial_state = 'scheduled'