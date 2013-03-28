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
        try:
            self.connection.layer.describe_domain(self.name)
        except SWFResponseError as e:
            # If resource does not exist, amazon throws 400 with
            # UnknownResourceFault exception
            if e.body['__type'] == 'com.amazonaws.swf.base.model#UnknownResourceFault':
                return False
            # Any other errors should raise
            else:
                raise e

        return True

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
