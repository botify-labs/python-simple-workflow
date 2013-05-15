#! -*- coding: utf-8 -*-

from swf.models.history import History
from swf.actors.core import Actor
from swf.exceptions import PollTimeout
from swf.models.decision.task import ActivityTaskDecision


class Decider(Actor):
    """Decider actor implementation

    :param  domain: Domain the Actor should interact with
    :type   domain: swf.models.Domain

    :param  task_list: task list the Actor should watch for tasks on
    :type   task_list: string

    :param  last_token: last seen task token
    :type   last_token: string
    """
    def __init__(self, domain, task_list):
        super(Decider, self).__init__(
            domain,
            task_list
        )

    def complete(self, task_token,
                 decisions=None, execution_context=None):
        """Responds to ``swf`` decisions have been made about
        the task with `task_token``

        :param  task_token: completed decision task token
        :type   task_token: string

        :param  decisions: The list of decisions (possibly empty)
                           made by the decider while processing this decision task
        :type   decisions: list (of swf.models.decision.Decision)
        """
        self.connection.respond_decision_task_completed(
            task_token,
            decisions,
            execution_context,
        )

    def poll(self, task_list=None,
             identity=None,
             maximum_page_size=None):
        """Polls for decision tasks to process from current
        actor's instance defined ``task_list``

        :param task_list: task list to poll for decision tasks from.
        :type task_list: string

        :param identity: Identity of the decider making the request,
        which is recorded in the DecisionTaskStarted event in the
        workflow history.
        :type identity: string

        :param maximum_page_size: The maximum number of history events
        returned in each page. The default is 100.
        :type maximum_page_size: integer

        :returns: polled decision tasks
        :type: swf.models.History
        """
        task_list = task_list or self.task_list

        events = self.connection.poll_for_decision_task(
            self.domain.name,
            task_list=task_list,
            identity=identity,
            maximum_page_size=maximum_page_size
        )

        if not 'taskToken' in events:
            raise PollTimeout("Decider poll timed out")

        history = History.from_event_list(events['events'])
        task_token = events['taskToken']

        return task_token, history