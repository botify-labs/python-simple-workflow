# -*- coding:utf-8 -*-

import unittest2

from mock import patch
from boto.exception import SWFResponseError
from boto.swf.exceptions import SWFTypeAlreadyExistsError

from swf.exceptions import AlreadyExistsError, DoesNotExistError
from swf.models.event import History
from swf.models.domain import Domain
from swf.models.workflow import WorkflowType, WorkflowExecution

from ..mocks.event import mock_get_workflow_execution_history


class TestWorkflowType(unittest2.TestCase):
    def setUp(self):
        self.domain = Domain("test-domain")
        self.wt = WorkflowType(self.domain, "TestType", "1.0")

    def tearDown(self):
        pass

    def test_init_with_invalid_child_policy(self):
        with self.assertRaises(ValueError):
            WorkflowType(
                self.domain,
                "TestType",
                "1.0",
                child_policy="FAILING_POLICY"
            )

    def test_save_already_existing_type(self):
        with patch.object(self.wt.connection, 'register_workflow_type') as mock:
            with self.assertRaises(AlreadyExistsError):
                mock.side_effect = SWFTypeAlreadyExistsError(400, "mocked exception")
                self.wt.save()

    def test_save_with_response_error(self):
        with patch.object(self.wt.connection, 'register_workflow_type') as mock:
            with self.assertRaises(DoesNotExistError):
                mock.side_effect = SWFResponseError(
                    400,
                    "mocked exception",
                    {
                        "__type": "UnknownResourceFault",
                        "message": "Whatever"
                    }
                )
                self.wt.save()

    def test_delete_non_existent_type(self):
        with patch.object(self.wt.connection, 'deprecate_workflow_type') as mock:
            with self.assertRaises(DoesNotExistError):
                mock.side_effect = SWFResponseError(
                    400,
                    "mocked exception",
                    {
                        "__type": "UnknownResourceFault",
                        "message": "Whatever"
                    }
                )
                self.wt.delete()

    def test_delete_deprecated_type(self):
        with patch.object(self.wt.connection, 'deprecate_workflow_type') as mock:
            with self.assertRaises(DoesNotExistError):
                mock.side_effect = SWFResponseError(
                    400,
                    "mocked exception",
                    {
                        "__type": "TypeDeprecatedFault",
                        "message": "Whatever"
                    }
                )
                self.wt.delete()


class TestWorkflowExecution(unittest2.TestCase):
    def setUp(self):
        self.domain = Domain("TestDomain")
        self.wt = WorkflowType(self.domain, "TestType", "1.0")
        self.we = WorkflowExecution(
            self.domain,
            self.wt,
            "TestType-0.1-TestDomain"
        )

    def tearDown(self):
        pass

    def test_instantiation(self):
        we = WorkflowExecution(
            self.domain,
            self.wt,
            "TestType-0.1-TestDomain"
        )
        self.assertIsNotNone(we)
        self.assertIsInstance(we, WorkflowExecution)
        self.assertIn(we.status, [
            WorkflowExecution.STATUS_OPEN,
            WorkflowExecution.STATUS_CLOSED
        ])

    def test_history(self):
        with patch.object(
            self.we.connection,
            'get_workflow_execution_history',
            mock_get_workflow_execution_history
        ):
            history = self.we.history()
            self.assertIsInstance(history, History)
