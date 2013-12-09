from . import step
from .proxy import Proxy
from .signal import SignalExecution


__all__ = ['Event']


class Event(Proxy):
    SUPPORTED = {'ActivityTask': step.ActivityStepExecution,
                 'ChildWorkflowExecution': step.WorkflowStepExecution,
                 'WorkflowExecution': step.WorkflowStepExecution,
                 'WorkflowExecutionSignaled': SignalExecution,
    }

    def __init__(self, raw_event):
        """
        :type raw_signal: swf.models.event.Event.

        """
        self._model = raw_event

    @classmethod
    def is_supported(cls, raw_event):
        """
        :type raw_signal: swf.models.event.Event.

        """
        return raw_event.type in cls.SUPPORTED

    def extract_from(self, workflow, history):
        """
        :rtype: Instruction | Signal

        """
        try:
            if self.type == 'WorkflowExecution' and self.state == 'signaled':
                signal_definition = workflow.signals[self.signal_name]
                return SignalExecution(signal_definition, history, self._model)
        except KeyError:
            raise ValueError(
                'signal {} is not supported by this workflow'.format(
                self.signal_name))

        try:
            return self.SUPPORTED[self.type](history, self._model)
        except KeyError:
            raise ValueError(
                'raw event {} in state {} is not supported'.format(
                self.type, self.state))
