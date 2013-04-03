# -*- coding: utf-8 -*-

from boto.swf.exceptions import SWFResponseError

from swf.querysets.base import BaseQuerySet
from swf.models.workflow import WorkflowType
from swf.exceptions import ResponseError, DoesNotExistError


class WorkflowTypeQuery(BaseQuerySet):
    def __init__(self, domain_name, *args, **kwargs):
        super(WorkflowTypeQuery, self).__init__(*args, **kwargs)
        self.domain_name = domain_name

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
            response = self.connection.describe_workflow_type(self.domain_name, name, str(version))
        except SWFResponseError as e:
            if e.error_code == 'UnknownResourceFault':
                raise DoesNotExistError(e.body['message'])

            raise ResponseError(e.body['message'])

        wt_info = response['typeInfo']
        wt_config = response['configuration']

        return WorkflowType(
            self.domain_name,
            wt_info['workflowType']['name'],
            int(wt_info['workflowType']['version']),
            status=wt_info['status'],
            task_list=wt_config['defaultTaskList']['name'],
            child_policy=wt_config['defaultChildPolicy'],
            execution_timeout=wt_config['defaultExecutionStartToCloseTimeout'],
            decision_task_timeout=wt_config['defaultTaskStartToCloseTimeout'],
        )

    def filter(self, domain_name=None, registration_status=WorkflowType.REGISTERED, name=None):
        """Filters workflows based of their status, and/or name"""
        workflow_types = []
        next_page_token = None

        # As WorkflowTypeQuery has to be built against a specific domain
        # name, domain filter is disposable, but not mandatory.
        domain_name = domain_name or self.domain_name

        while True:
            response = self.connection.list_workflow_types(
                domain_name,
                registration_status,
                name=name,
                next_page_token=next_page_token
            )

            for workflow in response['typeInfos']:
                workflow_types.append(WorkflowType(
                    self.domain_name,
                    workflow['workflowType']['name'],
                    int(workflow['workflowType']['version']),
                    status=workflow['status'],
                ))

            if not 'nextPageToken' in response:
                break

            next_page_token = response['nextPageToken']

        return workflow_types

    def all(self, registration_status=BaseQuerySet.REGISTERED_STATUS):
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
                self.domain_name,
                registration_status,
                next_page_token=next_page_token
            )

            for workflow in response['typeInfos']:
                workflow_types.append(WorkflowType(
                    self.domain_name,
                    workflow['workflowType']['name'],
                    int(workflow['workflowType']['version']),
                    status=workflow['status'],
                ))

            if not 'nextPageToken' in response:
                break

            next_page_token = response['nextPageToken']

        return workflow_types
