# -*- coding: utf-8 -*-

from boto.exception import SWFResponseError

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

    def __init__(self, name, status=REGISTERED, description=None,
                 retention_period=30, *args, **kwargs):
        super(Domain, self).__init__(*args, **kwargs)

        self.name = name
        self.status = status
        self.retention_period = retention_period
        self.description = description

    @requires_connection
    def save(self):
        """Creates the domain amazon side"""
        self.connection.layer.register_domain(self.name,
                                              self.retention_period,
                                              self.description)

    @requires_connection
    def delete(self):
        """Deprecates the domain amazon side"""
        self.connection.layer.deprecate_domain(self.name)
