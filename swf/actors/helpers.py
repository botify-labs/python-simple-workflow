#! -*- coding:utf-8 -*-

import time
import threading


class Heart(threading.Thread):
    """Implementation of an heart beating routine

    To be used by actors to send swf heartbeats notifications
    once in a while.

    :param  heartbeating_closure: Function to be called on heart
                                  beat tick. It takes not argument as input
    :type   heartbeating_closure: function

    :param  heartbeat_interval: interval between each heartbeats (in seconds)
    :type   heartbeat_interval: integer
    """

    def __init__(self, heartbeating_closure,
                 heartbeat_interval, *args, **kwargs):
        threading.Thread.__init__(self)

        self.heartbeating_closure = heartbeating_closure
        self.heartbeat_interval = heartbeat_interval
        self.keep_beating = True

    def stop(self):
        """Explicitly call for a heart stop.

        .join() method should be called after stop though.
        """
        self.keep_beating = False

    def run(self):
        while self.keep_beating is True:
            self.heartbeating_closure()
            time.sleep(self.heartbeat_interval)
