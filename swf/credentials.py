# -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

import os
from ConfigParser import ConfigParser

from boto.swf.layer1 import Layer1


def get_credentials_from_file(filepath):
    """Retrieves aws credentials from file

    provided file should be in ini format, and expose
    ``aws_access_key_id`` and ``aws_secret_access_key`` keys
    under ``credentials`` section.

    :param      filepath: file path to load credentials from
    :type       filepath: string

    :returns: ``aws_access_key_id`` ``aws_secret_access_key`` pair
    :rtype: tuple
    """
    try:
        fd = open(filepath, 'r')
    except IOError:
        return

    config = ConfigParser()
    config.readfp(fd)
    aws_access_key_id = config.get('credentials', 'aws_access_key_id')
    aws_secret_access_key = config.get('credentials', 'aws_secret_access_key')

    return (aws_access_key_id, aws_secret_access_key)


def get_credentials_from_env():
    """Retrieves aws credentials from environement

    ``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY``
    keys should be disposable through the environment.

    :returns: ``aws_access_key_id`` ``aws_secret_access_key`` pair
    :rtype: tuple
    """
    try:
        aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
        aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
    except KeyError:
        return (None, None)

    return aws_access_key_id, aws_secret_access_key


def extract_aws_credentials():
    """Tries to extract aws credentials from file or 
    from os environment.

    First, it will try to retrieve authentication credentials
    from a ``.swf`` file that should be placed in the user's
    base directory. *See swf.credentials.get_credentials_from_file
    for more details*.

    If no file were found, it will try to use credentials
    in os environment.

    If neither was present, then credentials are left set
    to None.

    :returns: credentials representation
    :rtype: dict
    """
    home_directory = os.environ['HOME']
    aws_credentials = dict().fromkeys([
        'aws_access_key_id',
        'aws_secret_access_key'
    ])

    credentials = get_credentials_from_file(
        os.path.join(home_directory, '.swf')
    )

    # if no valid credential file were found
    # then try to fetch them from environment
    if not credentials:
        credentials = get_credentials_from_env()

    aws_credentials['aws_access_key_id'] = credentials[0]
    aws_credentials['aws_secret_access_key'] = credentials[1]

    return aws_credentials

def set_aws_credentials(aws_access_key_id, aws_secret_access_key):
    """Set default credentials."""
    from swf.core import AWS_CREDENTIALS
    AWS_CREDENTIALS.update({
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key,
    })