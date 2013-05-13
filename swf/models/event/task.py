#! -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from swf.models.event.base import Event


class ActivityTaskEvent(Event):
    _type = 'ActivityTask'


class DecisionTaskEvent(Event):
    _type = 'DecisionTask'

    def __init__(self, *args, **kwargs):
        self.STATUS_TO_HANDLER = {
            'scheduled': self._handle_scheduled_state,
            'started': self._handle_started_state,
            'completed': self._handle_completed_state,
            'timeout': self._handle_timeout_state,
        }

        super(DecisionTaskEvent, self).__init__(*args, **kwargs)

    def from_data(self, data):
        self.STATUS_TO_HANDLER[self.state](data)

    def _handle_scheduled_state(self, data):
        self.dt_decided = data['eventTimestamp']

    def _handle_started_state(self, data):
        self.dt_decided = data['eventTimestamp']
        self.identity = data[self._attributes].get('identity')

    def _handle_completed_state(self, data):
        self.execution_context = data[self._attributes]['executionContext']

    def _handle_timeout_state(self, data):
        self.execution_context = data[self._attributes]['executionContext']