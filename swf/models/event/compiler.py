# -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from swf.models.event import Event


class InconsistentStateError(Exception):
    pass


class TransitionError(Exception):
    pass


class Stateful(object):
    states = ()
    transitions = {}


class CompiledEvent(Event, Stateful):
    initial_state = None

    def __init__(self, event):
        """Builds a  CompiledEvent from provided ``event``

        validates provided history event is in compiled event
        attended initial_state.

        :param  event: base event to build the compiled event upon
        :type   event: swf.models.event.Event
        """
        if event.state != self.initial_state:
            raise InconsistentStateError("Provided event is in %s state "
                                         "when attended intial state is %s"
                                         .format(event.state, self.initial_state))
        self.__dict__ = event.__dict__.copy()

    def __repr__(self):
        return '<CompiledEvent %s %s>' % (self.type, self.state)

    @property
    def next_states(self):
        return self.transitions[self.state]


    def transit(self, event):
        """Tries to apply CompiledEvent transition to the provided ``event``
        state

        :param  event: event to use in order to apply the compiled event
                       state transition
        :type   event: swf.models.event.Event
        """
        if event.state not in self.transitions[self.state]:
            raise TransitionError("Transition to state %s not allowed")

        self.__dict__ = event.__dict__.copy()
