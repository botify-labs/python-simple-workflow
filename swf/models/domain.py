# -*- coding: utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from boto.swf.exceptions import SWFResponseError, SWFDomainAlreadyExistsError

from swf.constants import REGISTERED
from swf.models import BaseModel
from swf.models.base import Diff
from swf.core import ConnectedSWFObject
from swf.exceptions import AlreadyExistsError, DoesNotExistError,\
                           ResponseError


class Domain(BaseModel):
    """Simple Workflow Domain wrapper

    :param      name: Name of the domain to register (unique)
    :type       name: string

    :param      retention_period: Domain's workflow executions records retention in days
    :type       retention_period: Integer

    :param      status: Specifies the registration status of the
                        workflow types to list. Valid values are:
                            * swf.constants.REGISTERED
                            * swf.constants.DEPRECATED
    :type       status: string

    :param      description: Textual description of the domain
    :type       description: string
    """
    def __init__(self, name,
                 status=REGISTERED,
                 description=None,
                 retention_period=30, *args, **kwargs):
        super(Domain, self).__init__(*args, **kwargs)

        self.name = name
        self.status = status
        self.description = description
        self.retention_period = retention_period

    def _diff(self):
        """Checks for differences between Domain instance
        and upstream version

        :returns: A list of swf.models.base.Diff namedtuple describing
                  differences
        :rtype: list
        """
        try:
            description = self.connection.describe_domain(self.name)
        except SWFResponseError as e:
            if e.error_code == 'UnknownResourceFault':
                raise DoesNotExistError("Remote Domain does not exist")
            else:
                raise ResponseError(e.body['message'])

        domain_info = description['domainInfo']
        domain_config = description['configuration']

        attributes_comparison = [
            Diff('name', self.name, domain_info['name']),
            Diff('status', self.status, domain_info['status']),
            Diff('description', self.description, domain_info['description']),
            Diff('retention_period', self.retention_period, domain_config['workflowExecutionRetentionPeriodInDays']),
        ]

        return filter(
            lambda data: data[1] != data[2],
            attributes_comparison
        )


    @property
    def exists(self):
        """Checks if the Domain exists amazon-side

        :rtype: bool
        """
        try:
            description = self.connection.describe_domain(self.name)
        except SWFResponseError as e:
            if e.error_code == 'UnknownResourceFault':
                return False
            else:
                raise ResponseError(e.body['message'])

        return True

    @property
    def is_synced(self):
        """Checks if Domain instance has changes, comparing
        with remote object representation

        :rtype: bool
        """
        return super(Domain, self).is_synced

    @property
    def changes(self):
        """Returns changes between Domain instance, and
        remote object representation

        :returns: A list of swf.models.base.Diff namedtuple describing
                  differences
        :rtype: list
        """
        return super(Domain, self).changes

    def save(self):
        """Creates the domain amazon side"""
        try:
            self.connection.register_domain(self.name,
                                            str(self.retention_period),
                                            self.description)
        except SWFDomainAlreadyExistsError:
            raise AlreadyExistsError("Domain %s already exists amazon-side" % self.name)

    def delete(self):
        """Deprecates the domain amazon side"""
        try:
            self.connection.deprecate_domain(self.name)
        except SWFResponseError as e:
            if e.error_code == 'UnknownResourceFault':
                raise DoesNotExistError("Domain %s does not exist amazon-side" % self.name)

    def workflows(self, status=REGISTERED):
        """Lists the current domain's workflow types

        :param      status: Specifies the registration status of the
                            workflow types to list. Valid values are:
                            * swf.constants.REGISTERED
                            * swf.constants.DEPRECATED
        :type       status: string
        """
        from swf.querysets.workflow import WorkflowTypeQuerySet
        qs = WorkflowTypeQuerySet(self)
        return qs.all(registration_status=status)

    @property
    def executions(self):
        pass

    def __repr__(self):
        return '<{} name={} status={}>'.format(
               self.__class__.__name__, self.name, self.status)
