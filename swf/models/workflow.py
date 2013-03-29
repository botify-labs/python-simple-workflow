# -*- coding:utf-8 -*-

from boto.swf.exceptions import SWFResponseError, SWFTypeAlreadyExistsError

from swf.core import ConnectedSWFObject
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
                 status=ConnectedSWFObject.REGISTERED,
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

    def start(self):
        """Starts a Workflow execution"""
        pass


class WorkflowExecution(ConnectedSWFObject):
    def __init__(self):
        pass