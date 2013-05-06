#! -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from swf.models.event.base import Event


class ActivityTaskEvent(Event):
    _type = 'ActivityTask'


class DecisionTaskEvent(Event):
    _type = 'DecisionTask'
