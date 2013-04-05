# -*- coding:utf-8 -*-

import unittest2
import boto.swf

from functools import partial
from mock import Mock, patch


from swf.core import set_aws_credentials
from swf.models.domain import Domain
from swf.querysets.domain import DomainQuerySet

from .mock_domain import mock_list_domains

set_aws_credentials('fakeaccesskey', 'fakesecretkey')


class TestDomain(unittest2.TestCase):
    def setUp(self):
        self.domain = Domain("testdomain")
        self.qs = DomainQuerySet(self.domain)

    def tearDown(self):
        pass

    def test_domain(self):
        pass
