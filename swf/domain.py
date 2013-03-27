# -*- coding: utf-8 -*-

from .constants import DOMAIN_REGISTERED
from .base import Connexion
from .utils import requires_connexion


class Domain(object):
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
    def __init__(self, name, retention_period,
                 description=None, *args, **kwargs):
        self._connexion = kwargs.pop('connexion', None)

        self.name = name
        self.retention_period = retention_period
        self.description = description

    @property
    def connexion(self):
        return self._connexion

    @connexion.setter
    def connexion(self, conn):
        if isinstance(conn, Connexion):
            self._connexion = conn

    @property
    @requires_connexion
    def exists(self):
        """Checks if the domain exists amazon-side"""
        domains = self.connexion.layer.list_domains(DOMAIN_REGISTERED)['domainInfos']

        return any(d['name'] == self.name for d in domains)

    @requires_connexion
    def save(self):
        """Creates the domain amazon side"""
        self.connexion.layer.register_domain(self.name,
                                             self.retention_period,
                                             self.description)

    @requires_connexion
    def deprecate(self):
        """Deprecates the domain amazon side"""
        self.connexion.layer.deprecate_domain(self.name)
