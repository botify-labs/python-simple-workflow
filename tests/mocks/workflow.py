# -*- coding:utf-8 -*-

from datetime import datetime

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
