# -*- coding:utf-8 -*-

import unittest2

from mock import patch
from boto.swf.layer1 import Layer1
from boto.swf.exceptions import SWFResponseError

from swf.models import Domain, ActivityType
from swf.exceptions import AlreadyExistsError, DoesNotExistError,\
                           ResponseError
from swf.models.base import Diff

from ..mocks.activity import mock_describe_activity_type

class TestActivityType(unittest2.TestCase):

    def setUp(self):
        self.domain = Domain("test-domain")
        self.activity_type = ActivityType(
            self.domain,
            "test-name",
            "test-version"
        )

    def tearDown(self):
        pass

    def test_activity_type__diff_with_different_activity_type(self):
        with patch.object(
            Layer1,
            'describe_activity_type',
            mock_describe_activity_type,
        ):
            activity = ActivityType(
                self.domain,
                "different-activity",
                version="different-version"
            )
            diffs = activity._diff()

            self.assertIsNotNone(diffs)
            self.assertEqual(len(diffs), 10)

            self.assertTrue(hasattr(diffs[0], 'attribute'))
            self.assertTrue(hasattr(diffs[0], 'local_value'))
            self.assertTrue(hasattr(diffs[0], 'remote_value'))

    def test_activity_type__diff_with_identical_activity_type(self):
        with patch.object(
            Layer1,
            'describe_activity_type',
            mock_describe_activity_type,
        ):
            mocked = mock_describe_activity_type()
            activity = ActivityType(
                self.domain,
                name=mocked['typeInfo']['activityType']['name'],
                version=mocked['typeInfo']['activityType']['version'],
                status=mocked['typeInfo']['status'],
                description=mocked['typeInfo']['description'],
                creation_date=mocked['typeInfo']['creationDate'],
                deprecation_date=mocked['typeInfo']['deprecationDate'],
                task_list=mocked['configuration']['defaultTaskList']['name'],
                task_heartbeat_timeout=mocked['configuration']['defaultTaskHeartbeatTimeout'],
                task_schedule_to_close_timeout=mocked['configuration']['defaultTaskScheduleToCloseTimeout'],
                task_schedule_to_start_timeout=mocked['configuration']['defaultTaskScheduleToStartTimeout'],
                task_start_to_close_timeout=mocked['configuration']['defaultTaskStartToCloseTimeout'],
            )

            diffs = activity._diff()

            self.assertEqual(diffs, [])

    def test_exists_with_existing_activity_type(self):
        with patch.object(Layer1, 'describe_activity_type'):
            self.assertTrue(self.activity_type.exists)

    def test_exists_with_non_existent_activity_type(self):
        with patch.object(self.activity_type.connection, 'describe_activity_type') as mock:
            mock.side_effect = SWFResponseError(
                    400,
                    "mocking exception",
                    {'__type': 'UnknownResourceFault'}
            )
            self.assertFalse(self.activity_type.exists)

    def test_activity_type_exists_with_whatever_error(self):
        with patch.object(self.activity_type.connection, 'describe_activity_type') as mock:
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

    def test_is_synced_with_unsynced_activity_type(self):
        pass

    def test_is_synced_with_synced_activity_type(self):
        pass

    def test_is_synced_over_non_existent_activity_type(self):
        with patch.object(
            Layer1,
            'describe_activity_type',
            mock_describe_activity_type
        ):
            domain = ActivityType(
                self.domain,
                "non-existent-activity",
                version="non-existent-version"
            )
            self.assertFalse(domain.is_synced)

    def test_changes_with_different_activity_type(self):
        with patch.object(
            Layer1,
            'describe_activity_type',
            mock_describe_activity_type,
        ):
            activity_type = ActivityType(
                self.domain,
                "different-activity-type",
                version="different-activity-type-version"
            )
            diffs = activity_type.changes

            self.assertIsNotNone(diffs)
            self.assertEqual(len(diffs), 10)

            self.assertTrue(hasattr(diffs[0], 'attribute'))
            self.assertTrue(hasattr(diffs[0], 'local_value'))
            self.assertTrue(hasattr(diffs[0], 'remote_value'))

    def test_activity_type_changes_with_identical_activity_type(self):
        with patch.object(
            Layer1,
            'describe_activity_type',
            mock_describe_activity_type,
        ):
            mocked = mock_describe_activity_type()
            activity_type = ActivityType(
                self.domain,
                name=mocked['typeInfo']['activityType']['name'],
                version=mocked['typeInfo']['activityType']['version'],
                status=mocked['typeInfo']['status'],
                description=mocked['typeInfo']['description'],
                creation_date=mocked['typeInfo']['creationDate'],
                deprecation_date=mocked['typeInfo']['deprecationDate'],
                task_list=mocked['configuration']['defaultTaskList']['name'],
                task_heartbeat_timeout=mocked['configuration']['defaultTaskHeartbeatTimeout'],
                task_schedule_to_close_timeout=mocked['configuration']['defaultTaskScheduleToCloseTimeout'],
                task_schedule_to_start_timeout=mocked['configuration']['defaultTaskScheduleToStartTimeout'],
                task_start_to_close_timeout=mocked['configuration']['defaultTaskStartToCloseTimeout'],
            )

            diffs = activity_type.changes

            self.assertEqual(diffs, [])
