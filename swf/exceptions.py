# -*- coding: utf-8 -*-


class InvalidCredentialsError(Exception):
    pass


class ResponseError(Exception):
    pass


class DoesNotExistError(Exception):
    pass


class AlreadyExistsError(Exception):
    pass


class InvalidKeywordArgumentError(Exception):
    pass
