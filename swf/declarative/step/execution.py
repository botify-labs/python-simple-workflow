import json

from ..proxy import Proxy

__all__ = ['Execution', 'WorkflowStepExecution', 'ActivityStepExecution']


class Execution(Proxy):
    """
    Represents the execution of a step.

    When a step is performed in a workflow, it takes different states (for
    example: ``scheduled``, ``started``, and ``completed``). All the states can
    be tracked in the workflow's history.

    """
    type = 'step'

    def __init__(self, history, raw_event):
        self._model = raw_event
        self._history = history

    @property
    def control(self):
        if self.state != 'scheduled':
            scheduled_event = self._history[self.scheduled_id]
            control = scheduled_event.control
        else:
            control = self._model.control

        return json.loads(control)

    @property
    def key(self):
        return self.control['key']

    @property
    def number(self):
        if hasattr(self._model, 'number'):
            return self._model.number

        return self.control['step_number']

    @property
    def retry(self):
        return self.control.get('retry', 0)

    @property
    def partition_id(self):
        return self.control.get('partition')

    def __repr__(self):
        return '<{} of {}>'.format(
               self.__class__.__name__, self._model)


class WorkflowStepExecution(Execution):
    @property
    def scheduled_as(self):
        return self.workflow_type['name']

    @property
    def scheduled_id(self):
        return self.initiated_event_id - 1


class ActivityStepExecution(Execution):
    @property
    def scheduled_as(self):
        scheduled_event = self._history[self.scheduled_id]
        return scheduled_event.activity_type['name']

    @property
    def scheduled_id(self):
        return self.scheduled_event_id - 1
