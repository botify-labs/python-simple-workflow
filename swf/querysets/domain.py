# -*- coding: utf-8 -*-

from boto.swf.exceptions import SWFResponseError

from swf.constants import REGISTERED
from swf.querysets.base import BaseQuerySet
from swf.models.domain import Domain
from swf.exceptions import (ResponseError, DoesNotExistError,
                            InvalidCredentialsError)


class DomainQuerySet(BaseQuerySet):
    """Swf domain queryset object

    Allows the user to interact with amazon's swf domains
    through a django-queryset like interface
    """
    def get(self, name):
        """Fetches the Domain with `name`

        A typical Amazon response looks like:
        {
            'configuration': {
                'workflowExecutionRetentionPeriodInDays': '7',
            },
            'domainInfo': {
                'status': 'REGISTERED',
                'name': 'CrawlTest',
                }
            }
        }
        """
        try:
            response = self.connection.describe_domain(name)
        except SWFResponseError as e:
            # If resource does not exist, amazon throws 400 with
            # UnknownResourceFault exception
            if e.error_code == 'UnknownResourceFault':
                raise DoesNotExistError("No such domain: %s" % name)
            elif e.error_code == 'UnrecognizedClientException':
                raise InvalidCredentialsError(
                    self.aws_access_key_id,
                    self.aws_secret_access_key
                )
            # Any other errors should raise
            raise ResponseError(e.body['message'])

        domain_info = response['domainInfo']
        domain_config = response['configuration']

        return Domain(
            domain_info['name'],
            status=domain_info['status'],
            retention_period=domain_config['workflowExecutionRetentionPeriodInDays'],
            connection=self.connection
        )

    def all(self, registration_status=REGISTERED):
        """Retrieves every domains

        A typical Amazon response looks like:
        {
            'domainInfos': [
                {
                    'name': 'Crawl'
                    'status': 'REGISTERED',
                    'description': '',
                },
            ]
        }
        """
        domains = []
        next_page_token = None

        while True:
            response = self.connection.list_domains(
                registration_status,
                next_page_token=next_page_token
            )

            domains.extend(
                [Domain(d['name'], d['status'], d['description']) for d
                 in response['domainInfos']]
            )

            if not 'nextPageToken' in response:
                break

            next_page_token = response['nextPageToken']

        return domains
