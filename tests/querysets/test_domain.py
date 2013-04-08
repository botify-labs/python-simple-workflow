# -*- coding:utf-8 -*-

import unittest2
import boto.swf

from functools import partial
from mock import Mock, patch


from swf.core import set_aws_credentials
from swf.models.domain import Domain
from swf.querysets.domain import DomainQuerySet

from .mock_domain import mock_list_domains, mock_describe_domain

set_aws_credentials('fakeaccesskey', 'fakesecretkey')


class TestDomainQuerySet(unittest2.TestCase):
    def setUp(self):
        self.domain = Domain("test-domain")
        self.qs = DomainQuerySet()

    def tearDown(self):
        pass

    def test_get_existent_domain(self):
        with patch.object(
            DomainQuerySet.connection,
            'describe_domain',
            mock_describe_domain
        ):
            domain = self.qs.get("test-domain")
            self.assertIsInstance(domain, Domain)

    def test_get_non_existent_domain(self):
        pass