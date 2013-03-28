# -*- coding: utf-8 -*-


class InvalidCredentialsError(Exception):
    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self.msg = "The credentials provided with this request are invalid. "\
                   "aws_access_key_id: %s, "\
                   "aws_secret_access_key: %s"\
                   % (aws_access_key_id, aws_secret_access_key)

    def __str__(self):
        return repr(self.msg)


class ResponseError(Exception):
    pass


class DoesNotExistError(Exception):
    pass


class AlreadyExistsError(Exception):
    pass
