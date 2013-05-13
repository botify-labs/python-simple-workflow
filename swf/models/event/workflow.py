#! -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from swf.models.event.base import Event


class WorkflowExecutionEvent(Event):
    _type = 'WorkflowExecution'

    def from_data(self, data):
        self.dt_started = data['eventTimestamp']

        self.execution_type = data[self._attributes]['workflowType']['name']
        self.execution_version = data[self._attributes]['workflowType']['version']
        self.task_list = data[self._attributes]['taskList']['name']

        self.input = data[self._attributes].get('input')

class ChildWorkflowExecutionEvent(Event):
    _type = 'ChildWorkflowExecution'


class ExternalWorkflowExecutionEvent(Event):
    _type = 'ExternalWorkflowExecution'
