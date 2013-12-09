from uuid import uuid4
import json

import swf.models

from ..proxy import Proxy
from ..constants import NB_ACTIVITY_TASKS_PER_DECISION


__all__ = ['Definition',  # Abstract class
           'WorkflowStepDefinition', 'ActivityStepDefinition',
           'GroupStepDefinition',
           'make']


class Definition(Proxy):
    """
    Abstract class that represents the definition of a step (see sub-classes).

    """
    type = 'step'

    def __init__(self, raw_step, input=None, output=None, retry=0):
        """
        :param raw_step: raw step definition
        :type  raw_step: swf.models.ActivityType | swf.models.WorkflowType

        :param input: names of the input parameters of a step
        :type  input: [str]

        :param output: names of the output parameters of a step
        :type  output: [str]

        """
        self._model = raw_step
        self._input = input
        self._output = output
        self._retry = retry

        self.name = self._model.name

    def __str__(self):
        # Using getattr over a property raises. That's why
        # _model private attr was directly used.
        timeout_fields = ('='.join([field_name, str(getattr(self._model, field_name))]) for
                          field_name in dir(self.model) if
                          not callable(field_name) and 'timeout' in field_name)

        return '<Step {name} {timeouts}>'.format(
            name=self.name,
            timeouts=' '.join([field_attr for field_attr in timeout_fields]))

        self.name = self._model.name

    @property
    def input(self):
        return self._input

    @property
    def output(self):
        return self._output

    @property
    def retry(self):
        return self._retry

    def prepare_input(self, context):
        if not self.input:
            return {}

        input = {}
        for key in self.input:
            try:
                eq_index = key.index('=')
            except(ValueError) as err:
                if str(err) != 'substring not found':
                    raise

                input[key] = context[key]
                continue

            name = key[:eq_index].strip()
            value = key[eq_index + 1:].strip()
            input[name] = value

        return input

    def schedule(self, history, context, control=None):
        raise NotImplementedError()

    def __repr__(self):
        return '<{} of {}>'.format(
               self.__class__.__name__, self._model)


class WorkflowStepDefinition(Definition):
    """
    Represents an step that executes a child workflow.

    """
    model = swf.models.workflow.WorkflowType

    def schedule(self, history, context, control=None):
        """Start a child workflow execution decision helper method.

        :param  workflow: Workflow type of the child workflow execution
                          to start.
        :type   workflow: swf.models.workflow.WorkflowType

        :param  input: values (serialized as a string) of the workflow
        :type   input: str

        """
        if control is None:
            control = {}

        control['step_number'] = self.number
        if 'retry' not in control:
            control['retry'] = getattr(self, 'retry', 0)

        workflow_id = context.get('__workflow_id__',
                                  '{}-{}'.format(self.name, uuid4()))
        return [swf.models.decision.ChildWorkflowExecutionDecision(
            'start',
            workflow_type=self._model,
            workflow_id=workflow_id,
            tag_list=context.get('__workflow_tag_list__'),
            control=json.dumps(control),
            execution_timeout=self.execution_timeout,
            task_list=self.task_list.format(**(context or {})),
            input=self.prepare_input(context)
        )]


class ActivityStepDefinition(Definition):
    """
    Represents a step that executes an activity task.

    """
    model = swf.models.ActivityType

    def schedule(self, history, context, control=None):
        """Schedule activity task decision helper method.

        :param  activity: Activity type of the task to schedule
        :type   activity: swf.models.activity.ActivityType

        :param  input: value (serialized as a string) of the activity task
        :type   input: str

        """
        if control is None:
            control = {}

        control['step_number'] = self.number
        if 'retry' not in control:
            control['retry'] = getattr(self, 'retry', 0)

        return [swf.models.decision.ActivityTaskDecision(
            'schedule',
            '{}-{}'.format(self.name, uuid4()),
            self._model,
            control=json.dumps(control),
            task_list=self.task_list.format(**(context or {})),
            input=self.prepare_input(context),
            task_timeout=self.task_start_to_close_timeout,
            duration_timeout=self.task_schedule_to_close_timeout,
            schedule_timeout=self.task_schedule_to_start_timeout,
            heartbeat_timeout=self.task_heartbeat_timeout)]


class GroupStepDefinition(Definition):
    def __init__(self, key, step):
        self.key = key
        self.step = step
        self._model = self.step

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, number):
        self._number = number
        self.step.number = number

    def schedule_partition(self, partition_id, history, context, control=None):
        local_context = context.copy()
        local_context[self.key] = partition_id

        local_control = control.copy()
        local_control['partition'] = partition_id
        return self.step.schedule(history,
                                  local_context,
                                  control=local_control)

    def activities(self, history, context):
        from ..event import Event

        for event in history.filter(type='ActivityTask'):
            step_execution = Event(event).extract_from({}, history)
            if step_execution.number != self.number:
                continue

            yield step_execution

    def remaining_partitions(self, history, context):
        all_partitions = set(context[self.key])

        activities = list(self.activities(history, context))
        completed = [activity.partition_id for activity in activities if
                     activity.state == 'completed']
        ongoing = [activity.partition_id for activity in activities if
                   activity.state in ('scheduled', 'started')]

        return all_partitions - set(completed) - set(ongoing)

    def schedule(self, history, context, control=None):
        """
        Schedule at most NB_ACTIVITY_TASKS_PER_DECISION partitions. Resume the
        scheduling of the remaining partitions until they have all completed.

        """
        if control is None:
            control = {}

        control['key'] = self.key

        remaining = self.remaining_partitions(history, context)
        if not remaining:
            return []

        decisions = []
        for key in list(remaining)[:NB_ACTIVITY_TASKS_PER_DECISION]:
            decisions.extend(self.schedule_partition(key,
                                                     history,
                                                     context,
                                                     control))

        return decisions


def make(raw_step, input=None, output=None, retry=0):
    for cls in Definition.__subclasses__():
        if isinstance(raw_step, cls.model):
            return cls(raw_step, input, output, retry)
    raise NotImplementedError('type {} not supported'.format(
                              type(raw_step)))
