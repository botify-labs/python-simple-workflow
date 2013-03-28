# -*- coding: utf-8 -*-

from swf.core import ConnectedSWFObject


class BaseQuerySet(ConnectedSWFObject):
    def get(self, name):
        raise NotImplemented

    def all(self):
        raise NotImplemented
