#! -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from gettext import gettext

import xworkflows

from swf.utils import Enum

_ = gettext


class EventState(xworkflows.Workflow):
    states = (
        (('start_requested'),   _('Start requested')),
        (('start_failed'),      _('Start failed')),
        (('started'),           _('Started')),
        (('stopped'),           _('Stopped')),
        (('cancel_requested'),  _('Cancel requested')),
        (('cancel_failed'),     _('Cancel failed')),
        (('canceled'),          _('Canceled')),
        (('ok'),                _('Ok')),
        (('failed'),            _('Failed')),
        (('timeout'),           _('Timeout')),
        (('signaled'),          _('Signaled')),
    )

    initial_state = 'stopped'

