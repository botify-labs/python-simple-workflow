# -*- coding:utf-8 -*-

import datetime

from swf.constants import REGISTERED
from swf.utils import datetime_timestamp
from swf.models.workflow import CHILD_POLICIES


def mock_list_workflow_types(*args, **kwargs):
    override_data = kwargs.pop('override_data', {})

    response = {
        "typeInfos": [
            {
                "creationDate": datetime_timestamp(datetime.now()),
                "deprecationDate": datetime_timestamp(datetime.now()),
                "description": "mocked workflow type",
                "status": REGISTERED,
                "workflowType": {
                    "name": "test-workflow type",
                    "version": "0.1",
                }
            }
        ]
    }

    response.update(override_data)

    return response


def mock_describe_workflow_type(*args, **kwargs):
    override_data = kwargs.pop('override_data', {})

    response = {
        "configuration": {
            "defaultChildPolicy": CHILD_POLICIES.TERMINATE,
            "defaultExecutionStartToCloseTimeout": "300",
            "defaultTaskList": {
                "name": "test-tasklist"
            },
            "defaultTaskStartToCloseTimeout": "300"
        },
        "typeInfo": {
            "creationDate": datetime_timestamp(datetime.now()),
            "deprecationDate": datetime_timestamp(datetime.now()),
            "description": "test-workflow-type",
            "status": REGISTERED,
            "workflowType": {
                "name": "test-workflow-type",
                "version": "0.1"
            }
        }
    }

    response.update(override_data)

    return response


def mock_get_workflow_execution_history(self, *args, **kwargs):
    override_data = kwargs.pop('override_data', {})

    response = {
        "events": [
            {
                'eventId': 1,
                'eventType': 'WorkflowExecutionStarted',
                'workflowExecutionStartedEventAttributes': {
                    'taskList': {
                        'name': 'test'
                    },
                    'parentInitiatedEventId': 0,
                    'taskStartToCloseTimeout': '300',
                    'childPolicy': 'TERMINATE',
                    'executionStartToCloseTimeout': '6000',
                    'workflowType': {
                        'version': '0.1',
                        'name': 'test-crawl-fsm1'
                    },
                },
                'eventTimestamp': 1365177769.585,
            },
            {
                'eventId': 2,
                'eventType': 'DecisionTaskScheduled',
                'decisionTaskScheduledEventAttributes': {
                    'startToCloseTimeout': '300',
                    'taskList': {
                        'name': 'test'
                    }
                },
                'eventTimestamp': 1365177769.585
            }
        ]
    }

    response.update(override_data)

    return response
