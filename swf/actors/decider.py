#! -*- coding: utf-8 -*-

from swf.models.event import History
from swf.actors.core import Actor


class Decider(Actor):
    """Decider actor implementation

    :param  domain: Domain the Actor should interact with
    :type   domain: swf.models.Domain

    :param  task_list: task list the Actor should watch for tasks on
    :type   task_list: string

    :param  last_token: last seen task token
    :type   last_token: string
    """
    def __init__(self, domain, task_list, last_token=None):
        super(Decider, self).__init__(
            domain,
            task_list,
            last_token
        )

    def complete(self, task_token=None, decisions=None, **kwargs):
        """Responds to ``swf`` a decision has been made

        :param  task_token: completed decision task token
        :type   task_token: string

        :param  decisions: The list of decisions (possibly empty)
                           made by the decider while processing this decision task
        :type   decisions: list
        """
        pass

    def poll(self, **kwargs):
        """Polls for decision tasks to process from current
        actor's instance defined ``task_list``

        :returns: polled decision tasks
        :type: swf.models.History
        """
        events = self.connection.poll_for_decision_task(
            self.domain.name,
            self.task_list
        )

        history = History.from_event_list(events['events'])
        self.task_token = events['taskToken']

        return history