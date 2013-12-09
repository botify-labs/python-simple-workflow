from .proxy import Proxy


class Signal(object):
    """
    Represents a signal that may interrupt a workflow.

    """
    type = 'signal'

    def __init__(self, name, target, input=None):
        """
        :type name: str
        :type input: [str]

        """
        self.name = name
        self.input = input
        self.target = target

    def __repr__(self):
        return '<{} {} with input={}>'.format(
               self.__class__.__name__, self.name, self.input)


class SignalExecution(Proxy):
    type = 'signal'

    def __init__(self, definition, history, raw_event):
        self._model = raw_event
        self._history = history
        self._definition = definition

    def trigger(self, context):
        return self._definition.target.schedule(context)
