# -*- coding: utf-8 -*-

from boto.swf.exceptions import SWFResponseError, SWFDomainAlreadyExistsError

from swf.constants import REGISTERED
from swf.core import ConnectedSWFObject
from swf.exceptions import AlreadyExistsError, DoesNotExistError


class Domain(ConnectedSWFObject):
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
        self.retention_period = retention_period
        self.description = description

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
