# -*- coding:utf-8 -*-

import unittest2

from mock import patch

from boto.swf.layer1 import Layer1
from boto.exception import SWFResponseError

from swf.core import set_aws_credentials
from swf.exceptions import (ResponseError, DoesNotExistError,
                            InvalidCredentialsError)
from swf.models.domain import Domain
from swf.models.activity import ActivityType
from swf.querysets.activity import ActivityTypeQuerySet

from ..mocks.activity import mock_list_activity_types,\
                           mock_describe_activity_type

set_aws_credentials('fakeaccesskey', 'fakesecretkey')


class TestActivityTypeQuerySet(unittest2.TestCase):

    def setUp(self):
        self.domain = Domain("TestDomain")
        self.atq = ActivityTypeQuerySet(self.domain)

    def tearDown(self):
        pass

    def test_get_domain_property_instantiates_private_attribute(self):
        """Assert .__init__() instantiate _domain private attr"""
        bw = ActivityTypeQuerySet(self.domain)
        delattr(bw, '_domain')
        bw.domain

        self.assertTrue(hasattr(bw, '_domain'))

    def test_instantiation_with_valid_domain(self):
        """Assert instantiation with valid domain object"""
        bw = ActivityTypeQuerySet(self.domain)

        self.assertIsInstance(bw.domain, Domain)
        self.assertEqual(bw._domain, bw.domain)

    def test_instantiation_with_invalid_domain(self):
        """Assert instantiation with invalid domain raises"""
        with self.assertRaises(TypeError):
            ActivityTypeQuerySet("WrongType")

    def test_all(self):
        """Asserts .all() method returns a list of valid Activity instances"""
        with patch.object(
            self.atq.connection,
            'list_activity_types',
            mock_list_activity_types,
        ):
            activities = self.atq.all()

            self.assertIsNotNone(activities)
            self.assertIsInstance(activities, list)

            for activity in activities:
                self.assertIsInstance(activity, ActivityType)

    def test_get_existent_activity_type(self):
        """Assert .get() method with valid params returns the asked ActivityType model"""
        with patch.object(
            self.atq.connection,
            'describe_activity_type',
            mock_describe_activity_type
        ):
            activity = self.atq.get('mocked-activity-type', '0.1')

            self.assertIsNotNone(activity)
            self.assertIsInstance(activity, ActivityType)

    def test_get_with_failing_activity_type(self):
        """Asserts get method over a failing activity type raises"""
        with patch.object(self.atq.connection, 'describe_activity_type') as mock:
            with self.assertRaises(ResponseError):
                mock.side_effect = SWFResponseError(
                    400,
                    'mocking exception',
                    {'__type': 'UnrecognizedClientException'}
                )

                self.atq.get('mocked-failing-activity-type', '0.1')

    def test_get_with_non_existent_name(self):
        """Asserts get method with non existent activity type name provided raises"""
        with patch.object(self.atq.connection, 'describe_activity_type') as mock:
            with self.assertRaises(DoesNotExistError):
                mock.side_effect = SWFResponseError(
                    400,
                    'mocking exception',
                    {'__type': 'UnknownResourceFault'}
                )
                self.atq.get('mocked-non-existent-activity-type-name', '0.1')

    def test_get_with_non_existent_version(self):
        """Asserts get method with non existent activity type version provided raises"""
        with patch.object(self.atq.connection, 'describe_activity_type') as mock:
            with self.assertRaises(DoesNotExistError):
                mock.side_effect = SWFResponseError(
                    400,
                    'mocking exception',
                    {'__type': 'UnknownResourceFault'}
                )
                self.atq.get('mocked-non-existent-activity-type-name', 'na')
