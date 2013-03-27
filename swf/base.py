# -*- coding:utf-8 -*-

import boto.swf


class Connection(object):
    """Holds an authenticated AWS Simple Workflow connexion

    Encapsulates a boto.swf.layer1 connexion object as `layer`
    attribute. Allows to access common swf api Layer1 methods
    through an authenticated session.

    Params
    ------
    * aws_access_key_id:
        * type: String
        * value: Aws access key id credential to authenticate with

    * aws_secret_access_key:
        * type: String
        * value: Aws secret access key to authenticate with
    """
    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.layer = self.authenticate()

    def authenticate(self):
        return boto.swf.layer1.Layer1(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )


class ConnectedSWFObject(object):
    def __init__(self, *args, **kwargs):
        self._connection = kwargs.pop('connection', None)

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, conn):
        if isinstance(conn, Connection):
            self._connexion = conn
