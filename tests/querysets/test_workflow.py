# -*- coding: utf-8 -*-

import unittest2

from mock import patch
from boto.exception import SWFResponseError

from swf.constants import REGISTERED
from swf.models.domain import Domain
from swf.models.workflow import WorkflowType
from swf.querysets.workflow import BaseWorkflowQuerySet,\
                                   WorkflowTypeQuerySet,\
                                   WorkflowExecutionQuerySet
from swf.exceptions import DoesNotExistError, ResponseError

from ..mocks.workflow import mock_describe_workflow_type,\
                             mock_list_workflow_types


class TestBaseWorkflowTypeQuerySet(unittest2.TestCase):

    def setUp(self):
        self.domain = Domain("TestDomain")
        self.bw = BaseWorkflowQuerySet(self.domain)

    def tearDown(self):
        pass

    def test_get_domain_property_instantiates_private_attribute(self):
        bw = BaseWorkflowQuerySet(self.domain)
        delattr(bw, '_domain')
        bw.domain

        self.assertTrue(hasattr(bw, '_domain'))

    def test_instantiation_with_valid_domain(self):
        bw = BaseWorkflowQuerySet(self.domain)

        self.assertIsInstance(bw.domain, Domain)
        self.assertEqual(bw._domain, bw.domain)

    def test_instantiation_with_invalid_domain(self):
        with self.assertRaises(TypeError):
            BaseWorkflowQuerySet("WrongType")

    def test__list_isnt_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.bw._list()


class TestWorkflowTypeQuerySet(unittest2.TestCase):

    def setUp(self):
        self.domain = Domain("TestDomain")
        self.wtq = WorkflowTypeQuerySet(self.domain)

    def tearDown(self):
        pass

    def test_valid_workflow_type(self):
        with patch.object(
            self.wtq.connection,
            'describe_workflow_type',
            mock_describe_workflow_type
        ):
            wt = self.wtq.get("TestType", "0.1")
            self.assertIsNotNone(wt)
            self.assertIsInstance(wt, WorkflowType)

    def test_get_non_existent_workflow_type(self):
        with patch.object(self.wtq.connection, 'describe_workflow_type') as mock:
            with self.assertRaises(DoesNotExistError):
                mock.side_effect = SWFResponseError(
                    400,
                    "mocked exception",
                    {
                        "__type": "UnknownResourceFault",
                        "message": "Whatever",
                    }
                )
                self.wtq.get("NonExistentWorkflowType", "0.1")

    def test_get_whatever_failing_workflow_type(self):
        with patch.object(self.wtq.connection, 'describe_workflow_type') as mock:
            with self.assertRaises(ResponseError):
                mock.side_effect = SWFResponseError(
                    400,
                    "mocked exception",
                    {
                        "__type": "Whatever Error",
                        "message": "Whatever",
                    }
                )
                self.wtq.get("NonExistentWorkflowType", "0.1")

    def test__list_non_empty_workflow_types(self):
        with patch.object(
            self.wtq.connection,
            'list_workflow_types',
            mock_list_workflow_types
        ):
            wt = self.wtq._list()
            self.assertIsNotNone(wt)
            self.assertIsInstance(wt, dict)

            for workflow in wt[WorkflowTypeQuerySet._infos_plural]:
                self.assertIsInstance(workflow, dict)

    def test_filter_with_registered_status(self):
        # Nota: mock_list_workfflow_types returned
        # values are REGISTERED
        with patch.object(
            self.wtq.connection,
            'list_workflow_types',
            mock_list_workflow_types
        ):
            types = self.wtq.filter(registration_status=REGISTERED)
            self.assertIsNotNone(types)
            self.assertIsInstance(types, list)

            for wt in types:
                self.assertIsInstance(wt, WorkflowType)
                self.assertEqual(wt.status, REGISTERED)