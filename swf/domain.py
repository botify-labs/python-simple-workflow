# -*- coding: utf-8 -*-

from .base import ConnectedSWFObject
from .utils import requires_connection


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

    def __init__(self, name, retention_period,
                 description=None, *args, **kwargs):
        super(Domain, self).__init__(*args, **kwargs)

        self.name = name
        self.retention_period = retention_period
        self.description = description

    @property
    @requires_connection
    def exists(self):
        """Checks if the domain exists amazon-side"""
        domains = self.connection.layer.list_domains(self.REGISTERED)['domainInfos']

        return any(d['name'] == self.name for d in domains)

    @requires_connection
    def save(self):
        """Creates the domain amazon side"""
        self.connection.layer.register_domain(self.name,
                                              self.retention_period,
                                              self.description)

    @requires_connection
    def deprecate(self):
        """Deprecates the domain amazon side"""
        self.connection.layer.deprecate_domain(self.name)
