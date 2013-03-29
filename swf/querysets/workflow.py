# -*- coding: utf-8 -*-

from boto.swf.exceptions import SWFResponseError

from swf.querysets.base import BaseQuerySet
from swf.models.workflow import WorkflowType
from swf.exceptions import ResponseError, DoesNotExistError


class WorkflowTypeQuery(BaseQuerySet):
    def __init__(self, domain, version, *args, **kwargs):
        super(WorkflowTypeQuery, self).__init__(*args, **kwargs)
        self.domain = domain
        self.version = version

    def get(self, name, version=None):
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
        version = version or self.version

        try:
            response = self.connection.describe_workflow_type(self.domain.name, name, str(version))
        except SWFResponseError as e:
            if e.error_code == 'UnknownResourceFault':
                raise DoesNotExistError(e.body['message'])
            else:
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
            else:
                next_page_token = response['nextPageToken']

        return workflow_types
