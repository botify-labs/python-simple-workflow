# -*- coding:utf-8 -*-

import boto.swf


class Workflow(object):
    def __init__(self, name, retention_period,
                 description=None, *args, **kwargs):
        self._connexion = kwargs.pop('connexion', None)

        self.name = name
        self.retention_period = retention_period
        self.description = description

