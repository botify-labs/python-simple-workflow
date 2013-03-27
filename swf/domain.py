# -*- coding: utf-8 -*-

from .constants import DOMAIN_REGISTERED
from .base import Connexion
from .utils import requires_connexion


class Domain(object):
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
        domains = self.connexion.layer.list_domains(DOMAIN_REGISTERED)['domainInfos']

        return any(d['name'] == self.name for d in domains)

    @requires_connexion
    def save(self):
        self.connexion.layer.register_domain(self.name,
                                             self.retention_period,
                                             self.description)

    @requires_connexion
    def deprecate(self):
        self.connexion.layer.deprecate_domain(self.name)
