# -*- coding:utf-8 -*-

from swf.constants import REGISTERED


def mock_list_domains(override_data={}, raises=None):
    if raises:
        raise raises(400, "Mocking exception raised")

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


def mock_describe_domain(override_data={}, raises=None):
    if raises:
        raise raises(400, "Mocking exception raised")

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
