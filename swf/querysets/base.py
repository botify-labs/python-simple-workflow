# -*- coding: utf-8 -*-

import boto.swf

from swf.core import ConnectedSWFObject


class BaseQuerySet(ConnectedSWFObject):
    @staticmethod
    def get(name):
        raise NotImplemented

    @staticmethod
    def all():
        raise NotImplemented