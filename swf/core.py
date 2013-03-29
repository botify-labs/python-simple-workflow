# -*- coding:utf-8 -*-

from boto.swf.layer1 import Layer1

AWS_CREDENTIALS = {
    'aws_access_key_id': None,
    'aws_secret_access_key': None
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
    REGISTERED = "REGISTERED"
    DEPRECATED = "DEPRECATED"

    def __init__(self, *args, **kwargs):
        for credkey in ('aws_access_key_id', 'aws_secret_access_key'):
            if AWS_CREDENTIALS.get(credkey):
                setattr(self, credkey, AWS_CREDENTIALS[credkey])

        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

        self.connection = Layer1(
            self.aws_access_key_id,
            self.aws_secret_access_key
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
