#! -*- coding: utf-8 -*-

import unittest2

from swf.models import Domain
from swf.actors import Actor
from swf.credentials import set_aws_credentials

set_aws_credentials('fakeaccesskey', 'fakesecret')


class TestActor(unittest2.TestCase):
    def setUp(self):
        self.domain = Domain("TestDomain")
        self.actor = Actor(self.domain, "test-task-list")

    def tearDown(self):
        pass

    def test_start_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.actor.start()

    def test_stop_alters_state(self):
        with self.assertRaises(NotImplementedError):
            self.actor.stop()
