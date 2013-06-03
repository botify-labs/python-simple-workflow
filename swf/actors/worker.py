#! -*- coding:utf-8 -*-

from swf.actors import Actor
from swf.models import ActivityTask
from swf.exceptions import PollTimeout


class ActivityWorker(Actor):
    """Activity task worker actor implementation

    Once started, will start polling for activity task,
    to process, and emitting heartbeat until it's stopped
    or crashes for some reason.

    :param  domain: Domain the Actor should interact with
    :type   domain: swf.models.Domain

    :param  task_list: task list the Actor should watch for tasks on
    :type   task_list: string

    :param  last_token: last seen task token
    :type   last_token: string
    """
    def __init__(self, domain, task_list):
        super(ActivityWorker, self).__init__(
            domain,
            task_list
        )

    def cancel(self, task_token, details=None):
        """Responds to ``swf`` that the activity task was canceled

        :param  task_token: canceled activity task token
        :type   task_token: string

        :param  details: provided details about cancel
        :type   details: string
        """
        return self.connection.respond_activity_task_canceled(task_token)

    def complete(self, task_token, result=None):
        """Responds to ``swf` that the activity task is completed

        :param  task_token: completed activity task token
        :type   task_token: string

        :param  result: The result of the activity task.
        :type   result: string
        """
        return self.connection.respond_activity_task_completed(
            task_token,
            result
        )

    def fail(self, task_token, details=None, reason=None):
        """Replies to ``swf`` that the activity task failed

        :param  task_token: canceled activity task token
        :type   task_token: string

        :param  details: provided details about cancel
        :type   details: string

        :param  reason: Description of the error that may assist in diagnostics
        :type   reason: string
        """
        return self.connection.respond_activity_task_failed(
            task_token,
            details,
            reason
        )

    def heartbeat(self, task_token, details=None):
        """Records activity task heartbeat

        :param  task_token: canceled activity task token
        :type   task_token: string

        :param  details: provided details about cancel
        :type   details: string
        """
        return self.connection.respond_activity_task_heartbeat(
            task_token,
            details
        )

    def poll(self, task_list=None, **kwargs):
        """Polls for an activity task to process from current
        actor's instance defined ``task_list``

        if no activity task was polled, raises a PollTimeout
        exception.

        :param  task_list: task list the Actor should watch for tasks on
        :type   task_list: string

        :raises: PollTimeout

        :returns: polled activity task
        :type: swf.models.ActivityTask
        """
        task_list = task_list or self.task_list

        polled_activity_data = self.connection.poll_for_activity_task(
            self.domain.name,
            task_list,
        )

        if not 'taskToken' in polled_activity_data:
            raise PollTimeout("Activity Worker poll timed out")

        activity_task = ActivityTask.from_poll(self.domain, self.task_list, polled_activity_data)
        task_token = activity_task.task_token

        return task_token, activity_task
