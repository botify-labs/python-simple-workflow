# -*- coding: utf-8 -*-

from boto.swf.exceptions import SWFResponseError

from swf.constants import REGISTERED
from swf.querysets.base import BaseQuerySet
from swf.models.workflow import WorkflowType, WorkflowExecution
from swf.utils import datetime_timestamp, past_day, get_subkey
from swf.exceptions import ResponseError, DoesNotExistError,\
                           InvalidKeywordArgumentError


class BaseWorkflowQuerySet(BaseQuerySet):
    """Base domain bounded workflow queryset objects

    Amazon workflows types and executions are always bounded
    to a specific domain: so any queryset which means to deal
    with workflows has to be built against a `domain`
    """
    def __init__(self, domain, *args, **kwargs):
        super(BaseWorkflowQuerySet, self).__init__(*args, **kwargs)
        self.domain = domain

    @property
    def domain(self):
        if not hasattr(self, '_domain'):
            self._domain = None
        return self._domain

    @domain.setter
    def domain(self, value):
        # Avoiding circular import
        from swf.models.domain import Domain

        if not isinstance(value, Domain):
            err = "domain property has to be of"\
                  "swf.model.domain.Domain type, not %r"\
                  % type(value)
            raise TypeError(err)
        self._domain = value


class WorkflowTypeQuerySet(BaseWorkflowQuerySet):
    def get(self, name, version):
        """Fetches the Workflow Type with `name` and `version`

        :param  name: name of the workflow type
        :type   name: String

        :param  version: workflow type version
        :type   version: String

        :returns: A swf.model.workflow.WorkflowType instance

        A typical Amazon response looks like:
        {
            'configuration': {
                'defaultExecutionStartToCloseTimeout': '300',
                'defaultTaskStartToCloseTimeout': '300',
                'defaultTaskList': {
                    'name': 'None'
                },
                'defaultChildPolicy': 'TERMINATE'
            },
            'typeInfo': {
                'status': 'REGISTERED',
                'creationDate': 1364492094.968,
                'workflowType': {
                    'version': '1',
                    'name': 'testW'
                }
            }
        }
        """
        try:
            response = self.connection.describe_workflow_type(self.domain.name, name, version)
        except SWFResponseError as e:
            if e.error_code == 'UnknownResourceFault':
                raise DoesNotExistError(e.body['message'])

            raise ResponseError(e.body['message'])

        wt_info = response['typeInfo']
        wt_config = response['configuration']

        return self.to_WorkflowType(
            wt_info,
            task_list=get_subkey(wt_config, ['defaultTaskList', 'name']),  # Avoid non-existing task-list
            child_policy=wt_config.get('defaultChildPolicy'),
            execution_timeout=wt_config.get('defaultExecutionStartToCloseTimeout'),
            decision_task_timeout=wt_config.get('defaultTaskStartToCloseTimeout'),
        )

    def to_WorkflowType(self, workflow_info, **kwargs):
        # Not using get_subkey in order for it to explictly
        # raise when workflowType name doesn't exist for example
        return WorkflowType(
            self.domain.name,
            workflow_info['workflowType']['name'],
            workflow_info['workflowType']['version'],
            status=workflow_info['status'],
            **kwargs
        )

    def filter(self, domain_name=None, registration_status=REGISTERED, name=None):
        """Filters workflows based of their status, and/or name"""

        def get_workflows():
            response = {'nextPageToken': None}
            while 'nextPageToken' in response:
                response = self.connection.list_workflow_types(
                    domain_name,
                    registration_status,
                    name=name,
                    next_page_token=response['nextPageToken']
                )

                for workflow in response['typeInfos']:
                    yield workflow

        # As WorkflowTypeQuery has to be built against a specific domain
        # name, domain filter is disposable, but not mandatory.
        domain_name = domain_name or self.domain.name

        return [self.to_WorkflowType(wf) for wf in get_workflows()]

    def all(self, registration_status=REGISTERED):
        """Retrieves every Workflow types

        A typical Amazon response looks like:
        {
            'typeInfos': [
                {
                    'status': 'REGISTERED',
                    'creationDate': 1364293450.67,
                    'description': '',
                    'workflowType': {
                        'version': '1',
                        'name': 'Crawl'
                    }
                },
                {
                    'status': 'REGISTERED',
                    'creationDate': 1364492094.968,
                    'workflowType': {
                        'version': '1',
                        'name': 'testW'
                    }
                }
            ]
        }
        """
        return self.filter(registration_status=registration_status)


class WorkflowExecutionQuerySet(BaseWorkflowQuerySet):
    """Fetches Workflow executions"""

    def _valid_list_operations_kwargs(self, status, kwargs):
        invalid_kwargs = []
        if status == WorkflowExecution.STATUS_OPEN:
            invalid_kwargs = [
                'start_latest_date',
                'start_oldest_date',
                'close_latest_date',
                'close_oldest_date',
                'close_status'
            ]
        else:
            invalid_kwargs = [
                'oldest_date',
                'latest_date'
            ]

        for kwarg in invalid_kwargs:
            if kwarg in kwargs:
                return False, kwarg

        return True, None

    def list_workflow_executions(self, status, *args, **kwargs):
        statuses = {
            WorkflowExecution.STATUS_OPEN: 'open',
            WorkflowExecution.STATUS_CLOSED: 'closed',
        }

        # boto.swf.list_closed_workflow_executions awaits a `start_oldest_date`
        # MANDATORY kwarg, when boto.swf.list_open_workflow_executions awaits a
        # `oldest_date` mandatory arg.
        if status == WorkflowExecution.STATUS_OPEN:
            oldest_date = kwargs.pop('start_oldest_date')
            args = args + (oldest_date,)

        method = 'list_{}_workflow_executions'.format(statuses[status])
        try:
            return getattr(self.connection, method)(*args, **kwargs)
        except KeyError:
            raise ValueError("Unknown status provided: %s" % status)

    def get_workflow_type(self, execution_info):
        workflow_type = execution_info.pop('workflowType')
        workflow_type_qs = WorkflowTypeQuerySet(self.domain)

        return workflow_type_qs.get(
            workflow_type['name'],
            workflow_type['version'],
        )

    def to_WorkflowExecution(self, execution_info, **kwargs):
        return WorkflowExecution(
            self.domain.name,
            self.get_workflow_type(execution_info),  # workflow_type
            get_subkey(execution_info, ['execution', 'workflowId']),  # workflow_id
            run_id=get_subkey(execution_info, ['execution', 'runId']),
            status=execution_info.get('executionStatus'),
            tag_list=execution_info.get('tagList'),
            **kwargs
        )

    def get(self, workflow_id, run_id):
        """ """
        try:
            response = self.connection.describe_workflow_execution(
                self.domain.name,
                run_id,
                workflow_id)
        except SWFResponseError as e:
            if e.error_code == 'UnknownResourceFault':
                raise DoesNotExistError(e.body['message'])

            raise ResponseError(e.body['message'])

        execution_info = response['executionInfo']
        execution_config = response['executionConfiguration']

        return self.to_WorkflowExecution(
            execution_info,
            task_list=get_subkey(execution_config, ['defaultTaskList', 'name']),
            child_policy=execution_config.get('childPolicy'),
            execution_timeout=execution_config.get('executionStartToCloseTimeout'),
            decision_tasks_timeout=execution_config.get('taskStartToCloseTimeout'),
        )

    def filter(self, domain_name=None,
               status=WorkflowExecution.STATUS_OPEN, tag=None,
               workflow_id=None, workflow_type_name=None,
               workflow_type_version=None,
               *args, **kwargs):
        """Filters workflow executions based on kwargs provided criteras

        :param  domain_name: workflow executions attached to domain with
                             provided domain_name will be kept
        :type   domain_name: String

        :param  status: workflow executions with provided status will be kept
        :type   status: swf.models.WorkflowExecution.{STATUS_OPEN, STATUS_CLOSED}

        :param  tag: workflow executions containing the tag will be kept
        :type   tag: String

        :param  workflow_id: workflow executions attached to the id will be kept
        :type   workflow_id: String

        :param  workflow_type_name: workflow executions attached to the workflow type
                                    with provided name will be kept
        :type   workflow_type_name: String

        :param  workflow_type_version: workflow executions attached to the workflow type
                                       of the provided version will be kept
        :type   workflow_type_version: String

        **Be aware that** querying over status allows the usage of statuses specific
        kwargs

        * STATUS_OPEN

            :param start_latest_date: latest start or close date and time to return (in days)
            :type  start_latest_date: int

        * STATUS_CLOSED

            :param  start_latest_date: workflow executions that meet the start time criteria
                                       of the filter are kept (in days)
            :type   start_latest_date: int

            :param  start_oldest_date: workflow executions that meet the start time criteria
                                       of the filter are kept (in days)
            :type   start_oldest_date: int

            :param  close_latest_date: workflow executions that meet the close time criteria
                                       of the filter are kept (in days)
            :type   close_latest_date: int

            :param  close_oldest_date: workflow executions that meet the close time criteria
                                       of the filter are kept (in days)
            :type   close_oldest_date: int

            :param  close_status: must match the close status of an execution for it
                                  to meet the criteria of this filter
            :type   close_status: swf.models.WorkflowExecution.{
                                      CLOSE_STATUS_COMPLETED,
                                      CLOSE_STATUS_FAILED,
                                      CLOSE_STATUS_CANCELED,
                                      CLOSE_STATUS_TERMINATED,
                                      CLOSE_STATUS_CONTINUED_AS_NEW,
                                      CLOSE_TIMED_OUT,
                                  }
        """

        def get_workflows(status, domain_name, **kwargs):
            response = {'nextPageToken': None}
            while 'nextPageToken' in response:
                response = self.list_workflow_executions(
                    status,
                    domain_name,
                    start_oldest_date=kwargs.pop('start_oldest_date'),
                    next_page_token=response['nextPageToken'],
                    **kwargs
                )

                for workflow in response['executionInfos']:
                    yield workflow

        valid_kwargs, invalid_kwarg = self._valid_list_operations_kwargs(status, kwargs)
        start_oldest_date = datetime_timestamp(past_day(kwargs.get('oldest_date', 30)))

        if not valid_kwargs:
            err_msg = "Invalid keyword argument supplied: {}".format(invalid_kwarg)
            raise InvalidKeywordArgumentError(err_msg)

        # As WorkflowTypeQuery has to be built against a specific domain
        # name, domain filter is disposable, but not mandatory.
        domain_name = domain_name or self.domain.name

        return [self.to_WorkflowExecution(wf) for wf
                in get_workflows(
                    status,
                    domain_name,
                    start_oldest_date=start_oldest_date)]

    def all(self, status=WorkflowExecution.STATUS_OPEN,
            start_oldest_date=30):
        """Fetch every workflow executions during the last `start_oldest_date`
        days, with `status`

        A typical amazon response looks like:

        .. code-block:: json

            {
                "executionInfos": [
                    {
                        "cancelRequested": "boolean",
                        "closeStatus": "string",
                        "closeTimestamp": "number",
                        "execution": {
                            "runId": "string",
                            "workflowId": "string"
                        },
                        "executionStatus": "string",
                        "parent": {
                            "runId": "string",
                            "workflowId": "string"
                        },
                        "startTimestamp": "number",
                        "tagList": [
                            "string"
                        ],
                        "workflowType": {
                            "name": "string",
                            "version": "string"
                        }
                    }
                ],
                "nextPageToken": "string"
            }

        :param  status: Workflow executions status filter
        :type   status: swf.models.WorkflowExecution.{STATUS_OPEN, STATUS_CLOSED}

        :param  start_oldest_date: Specifies the oldest start/close date to return.
        :type   start_oldest_date: integer (days)

        :returns: swf.model.WorkflowExcution objects list
        """
        workflow_executions = []
        next_page_token = None
        start_oldest_date = datetime_timestamp(past_day(start_oldest_date))

        while True:
            response = self.list_workflow_executions(
                status,
                self.domain.name,
                start_oldest_date=int(start_oldest_date),
                next_page_token=next_page_token
            )

            for execution_info in response['executionInfos']:
                workflow_executions.append(self.to_WorkflowExecution(execution_info))

            if not 'nextPageToken' in response:
                break

            next_page_token = response['nextPageToken']

        return workflow_executions
