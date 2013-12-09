import json
import sys
import traceback
import collections

import swf.models
import swf.utils
import swf.models.decision

from .history import History
from .event import Event


class Workflow(object):
    def __init__(self, name, version, domain, task_list, output_defs,
                 steps, signals, setup=None, teardown=None,
                 logger_name=None, *args, **kwargs):
        self.name = name
        self.version = version
        self.domain = domain
        self.task_list = task_list
        self.output_defs = output_defs
        self.steps = steps
        self.signals = signals

        self.setup = setup
        self.teardown = teardown

        self.log_format = ('[domain={}, workflow={}, version={}, '
                           'task_list={}] {{}}'.format(
                           self.domain.name, self.name, self.version,
                           self.task_list))
        self.logger = logging.getLogger(logger_name)

    def is_just_started(self, history):
        """Checks if the history state indicates the execution has just started

        :param  history: Workflow execution history to be checked against
        :type   history: swf.models.history.History
        """
        return len(history) == 3

    def handle_initialization(self, history):
        """
        :returns:
        :rtype: ([swf.models.decision.Decision], context)

        """
        workflow = history[0]
        context = getattr(workflow, 'input', {})
        if not isinstance(context, collections.Mapping):
            raise ValueError('workflow input must be a mapping (dict)')

        if self.setup:
            try:
                context = self.setup(context)
            except(Exception) as err:
                error = repr(traceback.format_exception(*sys.exc_info()))
                return self.fail(reason=str(err),
                                 details=error,
                                 context=context)

        try:
            context['__workflow_tag_list__'] = workflow.tag_list
        except(AttributeError):
            pass

        self.init(context)
        step = self.steps[0]
        decisions = step.schedule(history, context)

        return decisions, context

    def fail(self, reason, details, context):
        decision = swf.models.decision.WorkflowExecutionDecision()
        decision.fail(reason=reason[:256], details=details)

        context['__status__'] = 'FAILED'
        context['__reason__'] = reason
        context['__details__'] = details

        if self.teardown:
            try:
                self.teardown(context)
            except(Exception) as err:
                self.logger.error('cannot teardown workflow {}: {}'.format(
                                  self.name, err))
                pass

        return [decision], context

    def terminate(self, context):
        """Terminate workflow execution decision helper method

        :param  history: Workflow execution history to be checked against
        :type   history: swf.models.history.History

        :param  context:
        :type   context:
        """
        decision = swf.models.decision.WorkflowExecutionDecision()
        decision.complete(result=json.dumps({k: context[k] for k in
                                             self.output_defs}))

        if self.teardown:
            try:
                context = self.teardown(context)
            except(Exception) as err:
                context['__error__'] = str(err)

        return [decision], context

    def ignore(self, context):
        return [], context

    def init(self, context):
        """Initialize the context"""
        context['__status__'] = 'RUNNING'
        context['__current_step__'] = 0
        context['__ongoing_steps__'] = [0]

    def fetch(self, number):
        try:
            return self.steps[number]
        except IndexError:
            raise IndexError('invalid step number {}'.format(number))

    def current(self, context):
        """Returns the current number number from the context"""
        return context['__current_step__']

    def get_context(self, history):
        return json.loads(history.last_decision.execution_context or '{}')

    def schedule_next_step(self, current_step_number, history, context):
        try:
            current_step_number += 1
            step_definition = self.fetch(current_step_number)
            context['__current_step__'] = current_step_number
        except IndexError:
            return self.terminate(context)

        try:
            decisions = step_definition.schedule(history, context)
        except KeyError, err:
            reason = "variable '{}' is missing in context".format(
                     err.message)
            details = ''
            return self.fail(reason, details, context)

        context['__ongoing_steps__'].append(current_step_number)
        return decisions, context

    def handle_step_completed(self, step_execution, history, context):
        """
        :type step_execution: step.Execution

        :type history: History

        :returns:
        :rtype: ([swf.models.decision.Decision], context)

        """
        current_step_number = self.current(context)
        ongoing_steps = context['__ongoing_steps__']

        result = getattr(step_execution, 'result', {})
        if result:
            try:
                context.update({k: v for k, v in
                                json.loads(result).iteritems() if
                                not k.startswith('__')})
            except ValueError:  # JSON decoding error
                key = '_unknown_result@{}'.format(current_step_number)
                context[key] = result

        if step_execution.number not in ongoing_steps:  # i.e. is a signal
            self.logger.debug("{} {}#{} completed".format(
                step_execution.__class__.__name__,
                step_execution.scheduled_as,
                step_execution.number))

            return [], context

        decisions = []
        step_finished = True
        if step_execution.partition_id is not None:
            self.logger.debug("{} {}#{} (part #{}) completed".format(
                step_execution.__class__.__name__,
                step_execution.scheduled_as,
                step_execution.number,
                step_execution.partition_id))

            step = self.steps[step_execution.number]
            remaining = step.remaining_partitions(history, context)
            step_finished = not remaining
            if not step_finished:
                decisions.extend(step.schedule(history, context))

        if step_finished:
            self.logger.debug("{} {}#{} completed".format(
                step_execution.__class__.__name__,
                step_execution.scheduled_as,
                step_execution.number))

            context['__ongoing_steps__'].remove(step_execution.number)
            next_decisions, context = self.schedule_next_step(
                current_step_number,
                history,
                context)
            decisions.extend(next_decisions)

        return decisions, context

    def handle_step_timed_out(self, step_execution, history, context):
        scheduled_name = "{} '{}'".format(
                         step_execution.__class__.__name__,
                         step_execution.scheduled_as)

        scheduled_event = step_execution._history[step_execution.scheduled_id]
        timeout_type = step_execution.timeout_type.lower()

        self.log('error',
                 "step '{}' timed out on {} "
                 "(timeout={} seconds)".format(
                     scheduled_name,
                     timeout_type,
                     getattr(scheduled_event, '{}_timeout'.format(
                         timeout_type), 'N/A')))

        reason = "{} timed out".format(scheduled_name)
        return self.handle_failure(step_execution,
                                   history,
                                   context,
                                   reason=reason,
                                   details=timeout_type)

    def handle_step_failed(self, step_execution, history, context):
        scheduled_name = "{} '{}'".format(
                         step_execution.__class__.__name__,
                         step_execution.scheduled_as)
        reason = "{} failed".format(scheduled_name)
        self.log('error', reason)

        return self.handle_failure(step_execution,
                                   history,
                                   context,
                                   reason='error in {}: {}'.format(
                                       scheduled_name,
                                       step_execution.reason))

    def handle_failure(self, step_execution, history, context, reason='', details=''):
        if step_execution.number != self.current(context):
            return self.ignore(context)

        control = step_execution.control
        retry = control.get('retry', 0)
        if retry > 0:
            retry -= 1
            control['retry'] = retry

            step_definition = self.steps[step_execution.number]

            partition_id = control.get('partition')
            if partition_id is not None:
                decisions = step_definition.schedule_partition(partition_id,
                                                               context,
                                                               control)
            else:
                decisions = step_definition.schedule(history, context, control)
            return decisions, context

        return self.fail(reason[:256], details, context)

    def handle_step(self, step, history, context):
        """
        :type step: step.Execution

        :type history: History

        :returns:
        :rtype: ([swf.models.decision.Decision], context)

        It ignores the state that are not handled and returns an empty list of
        decisions.

        """
        try:
            handle = getattr(self, 'handle_step_{}'.format(
                                   step.state))
        except AttributeError:
            return [], context

        decisions, context = handle(step, history, context)
        return decisions, context

    def handle_signal(self, signal, history, context):
        if signal.input:
            input = json.loads(signal.input)
            if input:
                context.update(input)

        decisions = signal.trigger(context)
        return decisions, context

    def handle_event(self, raw_event, history, context):
        """
        :type raw_event: swf.models.event.Event

        :type history: History

        """
        action = Event(raw_event).extract_from(self, history)
        try:
            handle = getattr(self, 'handle_{}'.format(action.type))
        except AttributeError:
            raise NotImplementedError('event {} not supported'.format(
                                      action))

        return handle(action, history, context)

    def decide(self, history):
        """
        Interpret the history to return a set of decisions and a new context.

        It is usually called after a `poll()` returned, and returns `decisions`
        and `context` values suitables for `swf.actors.Decider.complete()`.

        At the moment, tasks executes sequentially i.e. next = current + 1.

        :returns:
        :rtype: ([swf.models.decision.Decision], context]) | None

        """
        # self.log('info', 'decision received')
        history = History(events=history.events)

        decisions = []
        context = {}
        try:
            try:
                history.last_decision
            except:
                decisions, context = self.handle_initialization(history)
            else:
                context = self.get_context(history)
            for event in (ev for ev in
                          history.events_since_last_decision):
                these_decisions, this_context = self.handle_event(
                    event, history, context)

                for decision in these_decisions:
                    if decision['decisionType'] == 'FailWorkflowExecution':
                        return [decision], context

                decisions.extend(these_decisions)
                context.update(this_context)

        except(Exception) as err:
            error = repr(traceback.format_exception(*sys.exc_info()))
            return self.fail(reason=repr(err),
                             details=error,
                             context=context)

        return decisions, context

    def log(self, level, msg):
        getattr(self.logger, level)(self.log_format.format(msg))

