# -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from boto.swf.layer1 import Layer1

from swf.credentials import extract_aws_credentials

AWS_CREDENTIALS = extract_aws_credentials()


class ConnectedSWFObject(object):
    """Authenticated object interface

    Once inherited, implements the AWS authentication
    into the child, adding a `connection` property.
    """
    __slots__ = [
        'region',
        'connection'
    ]

    def __init__(self, *args, **kwargs):
        self.region = kwargs.pop('region', None)

        self.connection = Layer1(
            AWS_CREDENTIALS['aws_access_key_id'],
            AWS_CREDENTIALS['aws_secret_access_key'],
            region=self.region
        )
