# -*- coding:utf-8 -*-

from swf.constants import REGISTERED


def mock_list_domains(override_data={}):
    response = {
        "domainInfos": [{
            "description": "mocked test domain",
            "name": "test-domain",
            "status": REGISTERED,
        }],
        "nextPageToken": "string"
    }

    response.update(override_data)

    return response


def mock_describe_domain(override_data={}):
    response = {
        "configuration": {
            "workflowExecutionRetentionPeriodInDays": "string"
        },
        "domainInfo": {
            "description": "string",
            "name": "string",
            "status": "string"
        }
    }

    response.update(override_data)

    return response
