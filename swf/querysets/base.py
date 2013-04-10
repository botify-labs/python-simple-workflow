# -*- coding: utf-8 -*-

from swf.core import ConnectedSWFObject


class BaseQuerySet(ConnectedSWFObject):
    def __init__(self, *args, **kwargs):
        super(BaseQuerySet, self).__init__(*args, **kwargs)

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def filter(self, *args, **kwargs):
        raise NotImplementedError

    def all(self, *args, **kwargs):
        raise NotImplementedError
