# -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from collections import namedtuple

from swf.core import ConnectedSWFObject


Diff = namedtuple('Diff', ['attribute', 'local_value', 'remote_value'])


class BaseModel(ConnectedSWFObject):

    def _diff(self):
        """Checks for differences between current model instance
        and upstream version"""
        raise NotImplementedError

    @property
    def exists(self):
        """Checks if the connected swf object exists amazon-side"""
        raise NotImplementedError


    @property
    def is_synced(self):
        """Checks if current Model instance has changes, comparing
        with remote object representation

        :rtype: bool
        """
        try:
            return bool(self._diff == [])
        except DoesNotExistError:
            return False

    @property
    def changes(self):
        """Returns changes between current model instance, and
        remote object representation

        :returns: A list of swf.models.base.Diff namedtuple describing
                  differences
        :rtype: list
        """
        return self._diff()

    def save(self):
        """Creates the connected swf object amazon side"""
        raise NotImplementedError

    def delete(self):
        """Deprecates the connected swf object amazon side"""
        raise NotImplementedError