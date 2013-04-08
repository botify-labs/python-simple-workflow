# -*- coding:utf-8 -*-

import unittest2

from mock import Mock, patch
from boto.swf.layer1 import Layer1
from boto.exception import SWFResponseError
from boto.swf.exceptions import SWFDomainAlreadyExistsError

from swf.core import set_aws_credentials
from swf.exceptions import AlreadyExistsError, DoesNotExistError
from swf.models.domain import Domain
from swf.querysets.domain import DomainQuerySet
from swf.querysets.workflow import WorkflowTypeQuerySet

from ..mocks import MiniMock

set_aws_credentials('fakeaccesskey', 'fakesecretkey')


class TestDomain(unittest2.TestCase):
    def setUp(self):
        self.domain = Domain("testdomain")
        self.qs = DomainQuerySet(self)

        self.mocked_workflow_type_qs = Mock(spec=WorkflowTypeQuerySet)
        self.mocked_workflow_type_qs.all.return_value = []

    def tearDown(self):
        pass

    @patch.object(
        Layer1,
        '__init__',
        MiniMock(
            aws_access_key_id='test',
            aws_secret_access_key='test'
        )
    )
    def test_domain_inits_connection(self):
        self.assertTrue(hasattr(self.domain, 'connection'))
        self.assertTrue(hasattr(self.domain.connection, 'aws_access_key_id'))
        self.assertTrue(hasattr(self.domain.connection, 'aws_secret_access_key'))

    def test_domain_save_valid_domain(self):
        with patch.object(self.domain.connection, 'register_domain') as mock:
            self.domain.save()

    def test_domain_save_already_existing_domain(self):
        with patch.object(self.domain.connection, 'register_domain') as mock:
            with self.assertRaises(AlreadyExistsError):
                mock.side_effect = SWFDomainAlreadyExistsError(400, "mocking exception")
                self.domain.save()

    def test_domain_delete_existing_domain(self):
        with patch.object(self.domain.connection, 'deprecate_domain') as mock:
            self.domain.delete()

    def test_domain_delete_non_existent_domain(self):
        with patch.object(self.domain.connection, 'deprecate_domain') as mock:
            with self.assertRaises(DoesNotExistError):
                mock.side_effect = SWFResponseError(
                    400,
                    "mocking exception",
                    {'__type': 'UnknownResourceFault'}
                )
                self.domain.delete()

    def test_domain_workflows_without_existent_workflows(self):
        with patch.object(WorkflowTypeQuerySet, 'all') as all_method:
            all_method.return_value = []
            self.assertEquals(self.domain.workflows(), [])