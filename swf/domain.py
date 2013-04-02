# -*- coding: utf-8 -*-

from .base import ConnectedSWFObject
from swf.querysets.domain import DomainQuery
from .utils import cached_property


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

    @cached_property
    def exists(self):
        return bool(DomainQuery(self.connection).get(self.name)):

    def save(self):
        """Creates the domain amazon side"""
        self.connection.register_domain(self.name,
                                        self.retention_period,
                                        self.description)

    def delete(self):
        """Deprecates the domain amazon side"""
        self.connection.deprecate_domain(self.name)
