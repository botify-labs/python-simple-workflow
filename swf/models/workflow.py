# -*- coding:utf-8 -*-

import time

from boto.swf.exceptions import SWFResponseError, SWFTypeAlreadyExistsError

from swf.constants import REGISTERED
from swf.core import ConnectedSWFObject
from swf.models.event import History
from swf.exceptions import DoesNotExistError, AlreadyExistsError


class WorkflowType(ConnectedSWFObject):
    """Simple Workflow Type wrapper

    Params
    ------
    * domain
        * type: swf.models.Domain
        * value: Domain the workflow type should be registered in
    * name
        * type: String
        * value: name of the workflow type
    * version
        * type: Integer
        * value: version of the workflow type
    * status
        * type: swf.core.ConnectedSWFObject.{REGISTERED, DEPRECATED}
        * value: workflow type status
    * task_list
        * type: String
        * value: task list to use for scheduling decision tasks for executions
                 of this workflow type
    * child_policy
        * type: swf.models.WorkflowType.{
                    CHILD_POLICY_TERMINATE,
                    CHILD_POLICY_REQUEST_CANCEL,
                    CHILD_POLICY_ABANDON
                }
        * value: policy to use for the child workflow executions
                 when a workflow execution of this type is terminated
    * execution_timeout
        * type: String
        * value: maximum duration for executions of this workflow type
    * decision_tasks_timeout
        * type: String
        * value: maximum duration of decision tasks for this workflow type
    * description
        * type: String
        * value:  Textual description of the workflow type
    """
    CHILD_POLICY_TERMINATE = "TERMINATE"  # child executions will be terminated
    CHILD_POLICY_REQUEST_CANCEL = "REQUEST_CANCEL"  #  a request to cancel will be attempted for each child execution
    CHILD_POLICY_ABANDON = "ABANDON"  # no action will be taken

    def __init__(self, domain, name, version,
                 status=REGISTERED,
                 task_list=None,
                 child_policy=CHILD_POLICY_TERMINATE,
                 execution_timeout='300',
                 decision_tasks_timeout='300',
                 description=None, *args, **kwargs):
        super(WorkflowType, self).__init__(*args, **kwargs)
        self.domain = domain
        self.name = name
        self.version = version
        self.status = status

        self._child_policy = None
        self.task_list = task_list
        self.execution_timeout = execution_timeout
        self.decision_tasks_timeout = decision_tasks_timeout
        self.description = description

        # Explicitly call child_policy setter
        # to validate input value
        self.child_policy = child_policy

    @property
    def child_policy(self):
        return self._child_policy

    @child_policy.setter
    def child_policy(self, value):
        valid_policies = [
            self.CHILD_POLICY_ABANDON,
            self.CHILD_POLICY_TERMINATE,
            self.CHILD_POLICY_REQUEST_CANCEL
        ]

        if value in valid_policies:
            self._child_policy = value
        else:
            raise ValueError("Provided child policy value is invalid")

    def save(self):
        """Creates the workflow type amazon side"""
        try:
            self.connection.register_workflow_type(
                self.domain.name,
                self.name,
                str(self.version),
                task_list=str(self.task_list),
                default_child_policy=str(self.child_policy),
                default_execution_start_to_close_timeout=str(self.execution_timeout),
                default_task_start_to_close_timeout=str(self.decision_tasks_timeout),
                description=self.description
            )
        except SWFTypeAlreadyExistsError:
            raise AlreadyExistsError("Workflow type %s already exists amazon-side" % self.name)
        except SWFResponseError as e:
            if e.error_code == 'UnknownResourceFault':
                raise DoesNotExistError(e.body['message'])

    def delete(self):
        """Deprecates the workflow type amazon-side"""
        try:
            self.connection.deprecate_workflow_type(self.domain.name, self.name, self.version)
        except SWFResponseError as e:
            if e.error_code in ['UnknownResourceFault', 'TypeDeprecatedFault']:
                raise DoesNotExistError(e.body['message'])

    def start_execution(self, workflow_id=None, task_list=None,
                        child_policy=None, execution_timeout=None,
                        input=None, tag_list=None, decision_tasks_timeout=None):
        """Starts a Workflow execution"""
        workflow_id = workflow_id or '%s-%s-%i' % (self.name, self.version, time.time())
        task_list = task_list or self.task_list
        child_policy = child_policy or self.child_policy

        run_id = self.connection.start_workflow_execution(
            self.domain.name,
            workflow_id,
            self.name,
            str(self.version),
            task_list=task_list,
            child_policy=child_policy,
            execution_start_to_close_timeout=execution_timeout,
            input=input,
            tag_list=tag_list,
            task_start_to_close_timeout=decision_tasks_timeout,
        )['runId']

        return WorkflowExecution(self.domain, workflow_id, run_id)

    def __repr__(self):
        return '<{} domain={} name={} version={} status={}>'.format(
               self.__class__.__name__,
               self.domain.name,
               self.name,
               self.version,
               self.status)


class WorkflowExecution(ConnectedSWFObject):
    STATUS_OPEN = "OPEN"
    STATUS_CLOSED = "CLOSED"

    CLOSE_STATUS_COMPLETED = "COMPLETED"
    CLOSE_STATUS_FAILED = "FAILED"
    CLOSE_STATUS_CANCELED = "CANCELED"
    CLOSE_STATUS_TERMINATED = "TERMINATED"
    CLOSE_STATUS_CONTINUED_AS_NEW = "CLOSE_STATUS_CONTINUED_AS_NEW"
    CLOSE_TIMED_OUT = "TIMED_OUT"

    def __init__(self, domain, workflow_id,
                 run_id=None, status=STATUS_OPEN,
                 *args, **kwargs):
        super(WorkflowExecution, self).__init__(*args, **kwargs)
        self.domain = domain
        self.workflow_id = workflow_id
        self.run_id = run_id or None
        self.status = status

    def history(self, *args, **kwargs):
        event_list = self.connection.get_workflow_execution_history(
            self.domain.name,
            self.run_id,
            self.workflow_id,
            **kwargs
        )['events']

        return History.from_event_list(event_list)
