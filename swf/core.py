# -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from boto.swf.layer1 import Layer1

AWS_CREDENTIALS = {
    #'aws_access_key_id': AWS_ACCESS_KEY_ID,
    #'aws_secret_access_key': AWS_SECRET_ACCESS_KEY,
}


def set_aws_credentials(aws_access_key_id, aws_secret_access_key):
    """Set default credentials."""
    AWS_CREDENTIALS.update({
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key,
    })


class ConnectedSWFObject(object):
    """Authenticated object interface

    Once inherited, implements the AWS authentication
    into the child, adding a `connection` property.
    """
    def __init__(self, *args, **kwargs):
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

        self.connection = Layer1(
            AWS_CREDENTIALS['aws_access_key_id'],
            AWS_CREDENTIALS['aws_secret_access_key'],
        )

