# -*- coding:utf-8 -*-

import boto.swf
from boto.swf.exceptions import SWFTypeAlreadyExistsError

from swf.core import ConnectedSWFObject
from swf.exceptions import DoesNotExistError, AlreadyExistsError


class WorkflowType(ConnectedSWFObject):
    CHILD_POLICY_TERMINATE = "TERMINATE"
    CHILD_POLICY_REQUEST_CANCEL = "REQUEST_CANCEL"
    CHILD_POLICY_ABANDON = "ABANDON"

    def __init__(self, domain, name, version,
                 task_list=None, child_policy=CHILD_POLICY_TERMINATE,
                 execution_timeout='300',
                 decision_tasks_timeout='300',
                 description=None, *args, **kwargs):
        super(WorkflowType, self).__init__(*args, **kwargs)
        self.domain = domain
        self.name = name
        self.version = version

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

    # def delete(self):
    #     try:
    #         self.connection.deprecate_workflow_type(self.domain.name, self.name, self.version)
    #     except SWFResponseError as e:
    #         if e.error_code == 'UnknownResourceFault':
    #             raise DoesNotExistError("Domain %s does not exist amazon-side" % self.name)

class WorkflowExecution(ConnectedSWFObject):
    def __init__(self):
        pass