#! -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from swf.models.event.states import EVENT_NAMES


class Event(object):
    """Simple workflow execution event wrapper

    :param      event_type: type of event represented.
                            Valid values are members of: swf.models.event.EVENT_TYPES
    :type       event_type: string

    :param      event_id: specifies a unique id for the event
    :type       event_id: int

    :param      event_timestamp: timestamp of the event trigger
    :type       event_timestamp: float
    """
    TYPES = EVENT_NAMES
    EVENT_ATTR_SUFFIX = 'EventAttributes'

    def __init__(self, event_type,
                 event_id=-1, event_timestamp=0.0,
                 *args, **kwargs):
        self._type = None

        self.id = event_id
        self.timestamp = event_timestamp
        self.type = event_type

        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

    def __repr__(self):
        return '<Event %s:%s>' % (self.type, self.id)

    @property
    def type(self):
        if not hasattr(self, '_type'):
            self._type = None
        return self._type

    @type.setter
    def type(self, value):
        if not value in Event.TYPES:
            raise ValueError("Invalid type supplied: %s" % self.type)
        self._type = value

    @classmethod
    def from_dict(cls, event_type,
                  event_id,
                  event_timestamp,
                  data,
                  *args, **kwargs):
        """Instantiates a new Event object from dictionary

        :param      event_type: type of event represented.
                                Valid values are members of: swf.models.event.EVENT_TYPES
        :type       event_type: string

        :param      event_id: specifies a unique id for the event
        :type       event_id: int

        :param      event_timestamp: timestamp of the event trigger
        :type       event_timestamp: float

        :param  data: event attributes data description
        :type   data: dict

        :returns: Event model instance built upon data
        :rtype  : swf.model.event.Event
        """
        return cls(event_type, event_id, event_timestamp, **data)