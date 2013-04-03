# -*- coding:utf-8 -*-

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

    def exists(self):
        """Checks if the connected swf object exists amazon-side"""
        raise NotImplemented

    def save(self):
        """Creates the connected swf object amazon side"""
        raise NotImplemented

    def deprecate(self):
        """Deprecates the connected swf object amazon side"""
        raise NotImplemented
