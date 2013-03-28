# -*- coding:utf-8 -*-

import boto.swf

from swf.core import ConnectedSWFObject


class WorkflowType(ConnectedSWFObject):
    def __init__(self, domain, name,
                 task_list=None, child_policy=None,
                 execution_timeout=None,
                 decision_tasks_timeout=None,
                 description=None):
        self.domain = domain
        self.name = name

        self.task_list = task_list
        self.child_policy = child_policy
        self.execution_timeout = execution_timeout
        self.decision_tasks_timeout = decision_tasks_timeout
        self.description = description


class WorkflowExecution(ConnectedSWFObject):
    def __init__(self):
        pass