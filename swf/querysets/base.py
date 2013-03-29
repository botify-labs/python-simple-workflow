# -*- coding: utf-8 -*-

from swf.core import ConnectedSWFObject


class BaseQuerySet(ConnectedSWFObject):
    REGISTERED_STATUS = "REGISTERED"
    DEPRECATED_STATUS = "DEPRECATED"

    def __init__(self, *args, **kwargs):
        super(BaseQuerySet, self).__init__(*args, **kwargs)

    def get(self, name):
        raise NotImplemented

    def all(self):
        raise NotImplemented
