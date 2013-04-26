#! -*- coding: utf-8 -*-

from swf.models.history import History
from swf.actors.core import Actor
from swf.exceptions import PollTimeout


class Decision(dict):
    pass

class DecisionsList(list):
    pass


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

    def schedule(self, activity_id, activity_type,
                 task_list=None,
                 control=None,
                 heartbeat_timeout='300',
                 schedule_to_close_timeout='300',
                 schedule_to_start_timeout='300',
                 start_to_close_timeout='300',
                 input=None):
        """Schedules an activity task

        :param  activity_id: Id the activity task to schedule
        :type   activity_id: string

        :param  activity_type: activity type of the task to schedule
        :type   activity_type: swf.models.ActivityType

        :param  task_list: task list the Actor should watch for tasks on
        :type   task_list: string

        :param  control: Optional data attached to the event that can be used
                         by the decider in subsequent workflow tasks.
        :type   control: string

        :param  heartbeat_timeout: specifies the maximum time before which
                                   a worker processing a task of this type must
                                   report progress by calling RecordActivityTaskHeartbeat
        :type   heartbeat_timeout: string

        :param  schedule_to_close_timeout:  The maximum duration for this activity task.
                                            The valid values are integers greater than or equal to 0.
                                            An integer value can be used to specify the duration in
                                            seconds while NONE can be used to specify unlimited duration.
        :type   schedule_to_close_timeout: string

        :param  schedule_to_start_timeout: specifies the maximum duration the activity task
                                           can wait to be assigned to a worker.
        :type   schedule_to_start_timeout: string

        :param  start_to_close_timeout:  specifies the maximum duration a worker may
                                         take to process this activity task.
        :type   start_to_close_timeout: string

        :param  input: The input provided to the activity task.
        :type   input: string

        :returns:
        :rtype: Decision
        """
        activity_type = {
            'name': activity_type.name,
            'version': activity_type.version
        }
        task_list = {'name': task_list } if task_list else None

        decision_attributes = {
            k:v for k, v in {
                'taskList': task_list,
                'activityId': activity_id,
                'activityType': activity_type,
                'control': control,
                'heartbeatTimeout': heartbeat_timeout,
                'scheduleToCloseTimeout': schedule_to_close_timeout,
                'scheduleToStartTimeout': schedule_to_start_timeout,
                'startToCloseTimeout': start_to_close_timeout,
                'input': input,
            }.iteritems() if v is not None
        }
        decision = Decision()
        decision['decisionType'] = 'ScheduleActivityTask'
        decision['scheduleActivityTaskDecisionAttributes'] = decision_attributes

        return decision


    def complete(self, task_token=None,
                 decisions=None, execution_context=None):
        """Responds to ``swf`` a decision has been made

        :param  task_token: completed decision task token
        :type   task_token: string

        :param  decisions: The list of decisions (possibly empty)
                           made by the decider while processing this decision task
        :type   decisions: Decisionslist
        """
        task_token = task_token or self.task_token

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
        self.task_token = events['taskToken']

        return history