# -*- coding: utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

class SWFError(Exception):
    def __init__(self, message, raw_error, *args):
        Exception.__init__(self, message, *args)
        self.kind, self.details = raw_error.split(':')

    def __repr__(self):
        msg = self.message

        if self.kind and self.details:
            msg += '\nReason: {}, {}'.format(self.kind, self.details)

        return msg

    def __str__(self):
        msg = self.message

        if self.kind and self.details:
            msg += '\nReason: {}, {}'.format(self.kind, self.details)

        return msg


class PollTimeout(SWFError):
    pass


class InvalidCredentialsError(SWFError):
    pass


class ResponseError(SWFError):
    pass


class DoesNotExistError(SWFError):
    pass


class AlreadyExistsError(SWFError):
    pass


class InvalidKeywordArgumentError(SWFError):
    pass
