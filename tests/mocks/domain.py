# -*- coding:utf-8 -*-

from swf.constants import REGISTERED


def mock_list_domains(*args, **kwargs):
    override_data = kwargs.pop('override_data', {})

    response = {
        "domainInfos": [{
            "description": "mocked test domain",
            "name": "test-domain",
            "status": REGISTERED,
        }],
        "nextPageToken": None
    }

    response.update(override_data)

    return response


def mock_describe_domain(*args, **kwargs):
    override_data = kwargs.pop('override_data', {})

    response = {
        "configuration": {
            "workflowExecutionRetentionPeriodInDays": "string"
        },
        "domainInfo": {
            "description": "mocked test domain",
            "name": "test-domain",
            "status": REGISTERED
        }
    }

    response.update(override_data)

    return response
