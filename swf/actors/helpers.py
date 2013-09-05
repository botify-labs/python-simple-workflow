#! -*- coding:utf-8 -*-

import time
import threading


class Heartbeater(threading.Thread):
    """Implementation of an heart beating routine

    To be used by actors to send swf heartbeats notifications
    once in a while.

    :param  heartbeat_closure: Function to be called on heart
                                  beat tick. It takes not argument as input
    :type   heartbeat_closure: function

    :param  task_token: task token the heartbeat is attached to
    :type   task_token: string

    :param  heartbeat_interval: interval between each heartbeats (in seconds)
    :type   heartbeat_interval: integer
    """
    def __init__(self, heartbeat_closure,
                 heartbeat_interval,
                 task_token=None,
                 *args, **kwargs):
        threading.Thread.__init__(self)

        self.heartbeat_closure = heartbeat_closure
        self.task_token = task_token
        self.heartbeat_interval = heartbeat_interval
        self.keep_beating = True

    def stop(self):
        """Explicitly call for a heart stop.

        .join() method should be called after stop though.
        """
        self.keep_beating = False

    def run(self):
        if not self.task_token:
            raise ValueError("Canno't start heartbeating without a "
                             "task_token set")

        while self.keep_beating is True:
            self.heartbeat_closure(self.task_token)
            time.sleep(self.heartbeat_interval)
