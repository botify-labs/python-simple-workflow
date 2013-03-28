# -*- coding: utf-8 -*-

from boto.swf.exceptions import SWFResponseError

from swf.exceptions import DoesNotExistError
from swf.querysets.base import BaseQuerySet
from swf.models.domain import Domain


class DomainQuery(BaseQuerySet):
    REGISTERED_STATUS = "REGISTERED"
    DEPRECATED_STATUS = "DEPRECATED"

    def get(self, name):
        try:
            response = self.connection.layer.describe_domain(name)
        except SWFResponseError as e:
            # If resource does not exist, amazon throws 400 with
            # UnknownResourceFault exception
            if e.body['__type'] == 'com.amazonaws.swf.base.model#UnknownResourceFault':
                raise DoesNotExistError("No such domain: %s" % name)
            # Any other errors should raise
            else:
                raise SWFResponseError(e.body['message'])

        domain_info = response['domainInfo']
        domain_config = response['configuration']

        return Domain(domain_info['name'], status=domain_info['status'],
                      retention_period=domain_config['workflowExecutionRetentionPeriodInDays'])

    def all(self, registration_status=REGISTERED_STATUS):
        domains = []
        next_page_token = None

        while True:
            response = self.connection.layer.list_domains(registration_status,
                                                          next_page_token=next_page_token)

            domains.extend([Domain(d['name'], d['status'], d['description']) for d
                            in response['domainInfos']])

            if not 'nextPageToken' in response:
                break
            else:
                next_page_token = response['nextPageToken']

        return domains
