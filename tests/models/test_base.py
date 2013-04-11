# -*- coding:utf-8 -*-

import unittest2

from boto.swf.layer1 import Layer1

from mock import patch

from swf.models import BaseModel


class TestBaseModel(unittest2.TestCase):

    def setUp(self):
        self.obj = BaseModel()

    def tearDown(self):
        pass

    def test__diff_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj._diff()

    def test_is_synced_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.is_synced

    def test_changes_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.changes


    def test_exists_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.exists

    def test_save_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.save()

    def test_delete_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.obj.delete()