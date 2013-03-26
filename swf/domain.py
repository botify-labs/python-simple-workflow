# -*- coding: utf-8 -*-

from .constants import DOMAIN_REGISTERED


class Domain(object):
    def __init__(self, name, retention_period,
                 description=None, *args, **kwargs):
        self.connexion = kwargs.pop('connexion')

        self.name = name
        self.retention_period = retention_period
        self.description = description

    @property
    def exists(self):
        domains = self.connexion.list_domains(DOMAIN_REGISTERED)['domainInfos']

        return any(d['name'] == self.name for d in domains)

    def save(self):
        self.connexion.register_domain(self.name,
                                       self.retention_period,
                                       self.description)

    def deprecate(self):
        self.connexion.deprecate_domain(self.name)
