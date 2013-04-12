# -*- coding:utf-8 -*-

import unittest2

from mock import patch
from boto.swf.layer1 import Layer1
from boto.exception import SWFResponseError
from boto.swf.exceptions import SWFTypeAlreadyExistsError

from swf.exceptions import AlreadyExistsError, DoesNotExistError, ResponseError
from swf.models.event import History
from swf.models.domain import Domain
from swf.models.workflow import WorkflowType, WorkflowExecution

from ..mocks.workflow import mock_describe_workflow_type
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

    def test___diff_with_different_workflow_type(self):
        with patch.object(
            Layer1,
            'describe_workflow_type',
            mock_describe_workflow_type,
        ):
            workflow_type = WorkflowType(
                self.domain,
                "different-workflow-type",
                version="different-version"
            )
            diffs = workflow_type._diff()

            self.assertIsNotNone(diffs)
            self.assertEqual(len(diffs), 6)

            self.assertTrue(hasattr(diffs[0], 'attribute'))
            self.assertTrue(hasattr(diffs[0], 'local_value'))
            self.assertTrue(hasattr(diffs[0], 'remote_value'))

    def test_workflow_type__diff_with_identical_workflow_type(self):
        with patch.object(
            Layer1,
            'describe_workflow_type',
            mock_describe_workflow_type,
        ):
            mocked = mock_describe_workflow_type()
            workflow_type = WorkflowType(
                self.domain,
                name=mocked['typeInfo']['workflowType']['name'],
                version=mocked['typeInfo']['workflowType']['version'],
                status=mocked['typeInfo']['status'],
                creation_date=mocked['typeInfo']['creationDate'],
                deprecation_date=mocked['typeInfo']['deprecationDate'],
                task_list=mocked['configuration']['defaultTaskList']['name'],
                child_policy=mocked['configuration']['defaultChildPolicy'],
                execution_timeout=mocked['configuration']['defaultExecutionStartToCloseTimeout'],
                decision_tasks_timeout=mocked['configuration']['defaultTaskStartToCloseTimeout'],
                description=mocked['typeInfo']['description'],
            )

            diffs = workflow_type._diff()

            self.assertEqual(diffs, [])

    def test_exists_with_existing_workflow_type(self):
        with patch.object(Layer1, 'describe_workflow_type'):
            self.assertTrue(self.wt.exists)

    def test_exists_with_non_existent_workflow_type(self):
        with patch.object(self.wt.connection, 'describe_workflow_type') as mock:
            mock.side_effect = SWFResponseError(
                    400,
                    "mocking exception",
                    {'__type': 'UnknownResourceFault'}
            )
            self.assertFalse(self.wt.exists)

    def test_workflow_type_exists_with_whatever_error(self):
        with patch.object(self.wt.connection, 'describe_workflow_type') as mock:
            with self.assertRaises(ResponseError):
                mock.side_effect = SWFResponseError(
                        400,
                        "mocking exception",
                        {
                            '__type': 'WhateverError',
                            'message': 'Whatever'
                        }
                )
                self.domain.exists

    def test_is_synced_with_unsynced_workflow_type(self):
        pass

    def test_is_synced_with_synced_workflow_type(self):
        pass

    def test_is_synced_over_non_existent_workflow_type(self):
        with patch.object(
            Layer1,
            'describe_workflow_type',
            mock_describe_workflow_type
        ):
            workflow_type = WorkflowType(
                self.domain,
                "non-existent-workflow-type",
                version="non-existent-version"
            )
            self.assertFalse(workflow_type.is_synced)

    def test_changes_with_different_workflow_type(self):
        with patch.object(
            Layer1,
            'describe_workflow_type',
            mock_describe_workflow_type,
        ):
            workflow_type = WorkflowType(
                self.domain,
                "different-workflow-type-type",
                version="different-workflow-type-type-version"
            )
            diffs = workflow_type.changes

            self.assertIsNotNone(diffs)
            self.assertEqual(len(diffs), 6)

            self.assertTrue(hasattr(diffs[0], 'attribute'))
            self.assertTrue(hasattr(diffs[0], 'local_value'))
            self.assertTrue(hasattr(diffs[0], 'remote_value'))

    def test_workflow_type_changes_with_identical_workflow_type(self):
        with patch.object(
            Layer1,
            'describe_workflow_type',
            mock_describe_workflow_type,
        ):
            mocked = mock_describe_workflow_type()
            workflow_type = WorkflowType(
               self.domain,
                name=mocked['typeInfo']['workflowType']['name'],
                version=mocked['typeInfo']['workflowType']['version'],
                status=mocked['typeInfo']['status'],
                creation_date=mocked['typeInfo']['creationDate'],
                deprecation_date=mocked['typeInfo']['deprecationDate'],
                task_list=mocked['configuration']['defaultTaskList']['name'],
                child_policy=mocked['configuration']['defaultChildPolicy'],
                execution_timeout=mocked['configuration']['defaultExecutionStartToCloseTimeout'],
                decision_tasks_timeout=mocked['configuration']['defaultTaskStartToCloseTimeout'],
                description=mocked['typeInfo']['description'],
            )

            diffs = workflow_type.changes

            self.assertEqual(diffs, [])


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
