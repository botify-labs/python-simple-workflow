# -*- coding: utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.


class PollTimeout(Exception):
    pass


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
