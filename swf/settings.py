# -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

import os
from ConfigParser import ConfigParser


def from_stream(stream):
    """Retrieves AWS settings from a stream in INI format.

    Example:

    >>> from StringIO import StringIO
    >>> stream = StringIO('''
    ...
    ... [credentials]
    ... aws_access_key_id=KEY_ID
    ... aws_secret_access_key=SECRET
    ...
    ... [defaults]
    ... region=eu-west-1
    ...
    ... ''')
    >>> settings = from_stream(stream)
    >>> settings['aws_access_key_id'] == 'KEY_ID'
    True
    >>> settings['aws_secret_access_key'] == 'SECRET'
    True
    >>> settings['region'] == 'eu-west-1'
    True
    >>> stream = StringIO('''
    ...
    ... [credentials]
    ... aws_access_key_id=KEY_ID
    ... aws_secret_access_key=SECRET
    ...
    ... ''')
    >>> settings = from_stream(stream)
    >>> settings['aws_access_key_id'] == 'KEY_ID'
    True
    >>> settings['aws_secret_access_key'] == 'SECRET'
    True

    :param      stream: of chars in INI format.
    :type       stream: stream.

    :rtype: dict

    ..note:: some fields may be None.

    """
    config = ConfigParser(allow_no_value=True)
    config.readfp(stream)

    settings = {}

    if config.has_section('credentials'):
        settings.update({
            'aws_access_key_id': config.get('credentials',
                                            'aws_access_key_id'),
            'aws_secret_access_key': config.get('credentials',
                                                'aws_secret_access_key')
        })

    if config.has_section('defaults'):
        settings['region'] = config.get('defaults', 'region')

    return settings


def from_file(path):
    """Retrieves AWS settings from a file in INI format.

    :param      path: to file in INI format.
    :type       path: string.

    :rtype: dict

    Returns `{}` is there is no file. Let raise the underlying exception if it
    cannot load the file (permission denied, file is a directory, etc...)

    """
    if not os.path.exists(path):
        return {}

    with open(path) as stream:
        return from_stream(stream)


def from_env():
    """Retrieves AWS settings from environment.

    Supported environment variables are:
        - `AWS_ACCESS_KEY_ID`
        - `AWS_SECRET_ACCESS_KEY`
        - `AWS_DEFAULT_REGION`

    :rtype: dict

    """
    try:
        return {'aws_access_key_id': os.environ['AWS_ACCESS_KEY_ID'],
                'aws_secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
                'region': os.environ.get('AWS_DEFAULT_REGION')
        }
    except KeyError:
        return {}


def get(path='.swf'):
    """Retrieves settings from a file or the environment.

    First, it will try to retrieve settings from a *path* in the user's home
    directory. Other it tries to load the settings from the environment.

    If both return an empty dict, it will also return a empty dict.

    :rtype: dict

    """
    home_directory = os.environ['HOME']
    return from_file(os.path.join(home_directory, path)) or from_env()


def set(**settings):
    """Set settings"""
    from swf.core import SETTINGS
    SETTINGS.update({k: v for k, v in settings.iteritems() if v is not None})
