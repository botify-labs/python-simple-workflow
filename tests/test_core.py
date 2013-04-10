# -*- coding:utf-8 -*-

import unittest2

from boto.swf.layer1 import Layer1

from mock import patch

from swf.core import ConnectedSWFObject


class TestConnectedSWFObject(unittest2.TestCase):

    def setUp(self):
        self.obj = ConnectedSWFObject()

    def tearDown(self):
        pass

    def test_exists_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.exists()

    def test_exists_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.save()

    def test_exists_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.deprecate()