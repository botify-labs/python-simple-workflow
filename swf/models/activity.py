# -*- coding: utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from boto.swf.exceptions import SWFTypeAlreadyExistsError, SWFResponseError

from swf.constants import REGISTERED, DEPRECATED
from swf.models import BaseModel
from swf.models.base import Diff
from swf.core import ConnectedSWFObject
from swf.exceptions import AlreadyExistsError, DoesNotExistError, ResponseError


class ActivityType(BaseModel):
    """ActivityType wrapper

    :param  domain: Domain the workflow type should be registered in
    :type   domain: swf.models.Domain

    :param  name: name of the ActivityType
    :type   name: str

    :param  version: version of the ActivityType
    :type   version: str

    :param  status: ActivityType status
    :type   status: swf.constants.{REGISTERED, DEPRECATED}

    :param  description: ActivityType description
    :type   description: str | None

    :param   creation_date: creation date of the current ActivityType
    :type    creation_date: float (timestamp)

    :param   deprecation_date: deprecation date of ActivityType
    :type    deprecation_date: float (timestamp)

    :param  task_list: specifies the default task list to use for scheduling
                       tasks of this activity type.
    :type   task_list: str

    :param  task_heartbeat_timeout: default maximum time before which a worker
                                    processing a task of this type must report
                                    progress by calling RecordActivityTaskHeartbeat.
    :type   task_heartbeat_timeout: int

    :param  task_schedule_to_close_timeout: default maximum duration for a task
                                            of this activity type.
    :type   task_schedule_to_close_timeout: int

    :param  task_schedule_to_start_timeout: default maximum duration that a
                                            task of this activity type can wait
                                            before being assigned to a worker.
    :type   task_schedule_to_start_timeout: int

    :param   task_start_to_close_timeout: default maximum duration that a
                                          worker can take to process tasks of
                                          this activity type.
    :type    task_start_to_close_timeout: int
    """
    def __init__(self, domain, name, version,
                 status=REGISTERED,
                 description=None,
                 creation_date=0.0,
                 deprecation_date=0.0,
                 task_list=None,
                 task_heartbeat_timeout=0,
                 task_schedule_to_close_timeout=0,
                 task_schedule_to_start_timeout=0,
                 task_start_to_close_timeout=0,
                 *args, **kwargs):
        super(ActivityType, self).__init__(*args, **kwargs)

        self.domain = domain
        self.name = name
        self.version = version
        self.status = status
        self.description = description

        self.creation_date = creation_date
        self.deprecation_date = deprecation_date

        self.task_list = task_list
        self.task_heartbeat_timeout = task_heartbeat_timeout
        self.task_schedule_to_close_timeout = task_schedule_to_close_timeout
        self.task_schedule_to_start_timeout = task_schedule_to_start_timeout
        self.task_start_to_close_timeout = task_start_to_close_timeout

    def _diff(self):
        """Checks for differences between ActivityType instance
        and upstream version

        :returns: A list of swf.models.base.Diff namedtuple describing
                  differences
        :rtype: list
        """
        try:
            description = self.connection.describe_activity_type(
                self.name,
                self.name,
                self.version
            )
        except SWFResponseError as err:
            if err.error_code == 'UnknownResourceFault':
                raise DoesNotExistError("Remote ActivityType does not exist")
            else:
                raise ResponseError(err.body['message'])

        info = description['typeInfo']
        config = description['configuration']

        attributes_comparison = [
            Diff('name', self.name, info['activityType']['name']),
            Diff('version', self.version, info['activityType']['version']),
            Diff('status', self.status, info['status']),
            Diff('description', self.description, info['description']),
            Diff('creation_date', self.creation_date, info['creationDate']),
            Diff('deprecation_date', self.deprecation_date, info['deprecationDate']),
            Diff('task_list', self.task_list, config['defaultTaskList']['name']),
            Diff('task_heartbeat_timeout', self.task_heartbeat_timeout, config['defaultTaskHeartbeatTimeout']),
            Diff('task_schedule_to_close_timeout', self.task_schedule_to_close_timeout, config['defaultTaskScheduleToCloseTimeout']),
            Diff('task_schedule_to_start_timeout', self.task_schedule_to_start_timeout, config['defaultTaskScheduleToStartTimeout']),
            Diff('task_start_to_close_timeout', self.task_start_to_close_timeout, config['defaultTaskStartToCloseTimeout']),
        ]

        return filter(
            lambda data: data.local_value != data.remote_value,
            attributes_comparison
        )


    @property
    def exists(self):
        """Checks if the ActivityType exists amazon-side

        :rtype: bool
        """
        try:
            description = self.connection.describe_activity_type(
                self.domain.name,
                self.name,
                self.version
            )
        except SWFResponseError as err:
            if err.error_code == 'UnknownResourceFault':
                return False
            else:
                raise ResponseError(err.body['message'])

        return True

    @property
    def is_synced(self):
        """Checks if ActivityType instance has changes, comparing
        with remote object representation

        :rtype: bool
        """
        return super(ActivityType, self).is_synced

    @property
    def changes(self):
        """Returns changes between Domain instance, and
        remote object representation

        :returns: A list of swf.models.base.Diff namedtuple describing
                  differences
        :rtype: list
        """
        return super(ActivityType, self).changes

    def save(self):
        """Creates the activity type amazon side"""
        try:
            self.connection.register_activity_type(
                self.domain.name,
                self.name,
                self.version,
                task_list=str(self.task_list),
                default_task_heartbeat_timeout=str(self.task_heartbeat_timeout),
                default_task_schedule_to_close_timeout=str(self.task_schedule_to_close_timeout),
                default_task_schedule_to_start_timeout=str(self.task_schedule_to_start_timeout),
                default_task_start_to_close_timeout=str(self.task_start_to_close_timeout),
                description=self.description)
        except SWFTypeAlreadyExistsError, err:
            raise AlreadyExistsError('{} already exists'.format(self))
        except SWFResponseError as err:
            if err.error_code in ['UnknownResourceFault', 'TypeDeprecatedFault']:
                raise DoesNotExistError(err.body['message'])
            raise

    def delete(self):
        """Deprecates the domain amazon side"""
        try:
            self.connection.deprecate_activity_type(self.domain.name,
                                                 self.name,
                                                 self.version)
        except SWFResponseError as err:
            if err.error_code == 'UnknownResourceFault':
                raise DoesNotExistError("%s does not exist" % self)
        self.status = DEPRECATED

    def __repr__(self):
        return '<{} domain={} name={} version={} status={}>'.format(
               self.__class__.__name__,
               self.domain.name,
               self.name,
               self.version,
               self.status)
