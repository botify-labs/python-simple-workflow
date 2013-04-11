# -*- coding: utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from datetime import datetime, timedelta
from time import mktime

from functools import wraps

# De-capitalize a string (lower first character)
decapitalize = lambda s: s[:1].lower() + s[1:] if s else ''

# Get a past day datetime
past_day = lambda d: datetime.now() - timedelta(days=d)

# Get a datetime timestamp
datetime_timestamp = lambda datetime: mktime(datetime.timetuple())


def get_subkey(d, key_path):
    """Gets a sub-dict key, and return None if whether
    the parent or child dict key does not exist

    Example:
    >>> d = {
      'a': {
        '1': 2,
        '2': 3,
      }
    }
    >>> subkey(d, ['a'])
    {'1': 2, '2': 3}
    >>> subkey(d, ['a', '1'])
    2
    >>> subkey(d, ['a', '3'])
    None

    :param  d: dict to operate over
    :type   d: dict of dicts

    :param  key_path: dict keys path list representation
    :type   key_path: list
    """
    if len(key_path) > 1:
        if d.get(key_path[0]) is None:
            return None
        return get_subkey(d[key_path[0]], key_path[1:])
    else:
        return d.get(key_path[0])


class _CachedProperty(property):
    """A property cache mechanism.

    The cache is stored on the model as a protected attribute. Expensive
    property lookups, such as database access, can therefore be sped up
    when accessed multiple times in the same request.

    The property can also be safely set and deleted without interference.
    """

    def __init__(self, fget, fset=None, fdel=None, doc=None):
        """Initializes the cached property."""
        self._cache_name = "_{name}_cache".format(
            name=fget.__name__,
        )
        # Wrap the accessors.
        fget = self._wrap_fget(fget)
        if callable(fset):
            fset = self._wrap_fset(fset)
        if callable(fdel):
            fdel = self._wrap_fdel(fdel)
        # Create the property.
        super(_CachedProperty, self).__init__(fget, fset, fdel, doc)

    def _wrap_fget(self, fget):
        @wraps(fget)
        def do_fget(obj):
            if hasattr(obj, self._cache_name):
                return getattr(obj, self._cache_name)
            # Generate the value to cache.
            value = fget(obj)
            setattr(obj, self._cache_name, value)
            return value
        return do_fget

    def _wrap_fset(self, fset):
        @wraps(fset)
        def do_fset(obj, value):
            fset(obj, value)
            setattr(obj, self._cache_name, value)
        return do_fset

    def _wrap_fdel(self, fdel):
        @wraps(fdel)
        def do_fdel(obj):
            fdel(obj)
            delattr(obj, self._cache_name)
        return do_fdel
cached_property = _CachedProperty
