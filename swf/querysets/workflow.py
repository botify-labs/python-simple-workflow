# -*- coding: utf-8 -*-

from boto.swf.exceptions import SWFResponseError

from swf.constants import REGISTERED
from swf.querysets.base import BaseQuerySet
from swf.models.workflow import WorkflowType, WorkflowExecution
from swf.exceptions import ResponseError, DoesNotExistError
from swf.utils import datetime_timestamp, past_day


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
            response = self.connection.describe_workflow_type(self.domain.name, name, str(version))
        except SWFResponseError as e:
            if e.error_code == 'UnknownResourceFault':
                raise DoesNotExistError(e.body['message'])

            raise ResponseError(e.body['message'])

        wt_info = response['typeInfo']
        wt_config = response['configuration']

        return WorkflowType(
            self.domain.name,
            wt_info['workflowType']['name'],
            int(wt_info['workflowType']['version']),
            status=wt_info['status'],
            task_list=wt_config['defaultTaskList']['name'],
            child_policy=wt_config['defaultChildPolicy'],
            execution_timeout=wt_config['defaultExecutionStartToCloseTimeout'],
            decision_task_timeout=wt_config['defaultTaskStartToCloseTimeout'],
        )

    def filter(self, domain_name=None, registration_status=REGISTERED, name=None):
        """Filters workflows based of their status, and/or name"""
        workflow_types = []
        next_page_token = None

        # As WorkflowTypeQuery has to be built against a specific domain
        # name, domain filter is disposable, but not mandatory.
        domain_name = domain_name or self.domain.name

        while True:
            response = self.connection.list_workflow_types(
                domain_name,
                registration_status,
                name=name,
                next_page_token=next_page_token
            )

            for workflow in response['typeInfos']:
                workflow_types.append(WorkflowType(
                    self.domain.name,
                    workflow['workflowType']['name'],
                    int(workflow['workflowType']['version']),
                    status=workflow['status'],
                ))

            if not 'nextPageToken' in response:
                break

            next_page_token = response['nextPageToken']

        return workflow_types

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
        workflow_types = []
        next_page_token = None

        while True:
            response = self.connection.list_workflow_types(
                self.domain.name,
                registration_status,
                next_page_token=next_page_token
            )

            for workflow in response['typeInfos']:
                workflow_types.append(WorkflowType(
                    self.domain.name,
                    workflow['workflowType']['name'],
                    int(workflow['workflowType']['version']),
                    status=workflow['status'],
                ))

            if not 'nextPageToken' in response:
                break

            next_page_token = response['nextPageToken']

        return workflow_types


class WorkflowExecutionQuerySet(BaseWorkflowQuerySet):
    """Fetches Workflow executions"""

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

            for workflow in response['executionInfos']:
                print workflow['workflowType']
                workflow_type_qs = WorkflowTypeQuerySet(self.domain)
                workflow_type = workflow_type_qs.get(
                    workflow['workflowType']['name'],
                    int(workflow['workflowType']['version']),
                )

                workflow_executions.append(WorkflowExecution(
                    self.domain,
                    workflow_type,
                    workflow['execution']['workflowId'],
                    run_id=workflow['execution']['runId'],
                    status=workflow['executionStatus'],
                ))

            if not 'nextPageToken' in response:
                break

            next_page_token = response['nextPageToken']

        return workflow_executions
