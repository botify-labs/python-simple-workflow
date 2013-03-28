# -*- coding: utf-8 -*-

from boto.swf.exceptions import SWFResponseError, SWFDomainAlreadyExistsError

from swf.core import ConnectedSWFObject
from swf.exceptions import AlreadyExistsError, DoesNotExistError


class Domain(ConnectedSWFObject):
    """Simple Workflow Domain wrapper

    Params
    ------
    * name:
        * type: String
        * value: Name of the domain to register (unique)

    * retention_period
        * type: Integer
        * value: Domain's workflow executions records retention in days

    * description
        * type: String
        * value: Textual description of the domain
    """
    REGISTERED = "REGISTERED"
    DEPRECATED = "DEPRECATED"

    def __init__(self, name, status=REGISTERED, description=None,
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

    @property
    def workflows(self):
        pass

    @property
    def executions(self):
        pass
