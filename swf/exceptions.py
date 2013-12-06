# -*- coding: utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.


class SWFError(Exception):
    def __init__(self, message, raw_error='', *args, **kwargs):
        """
        Examples:

        >>> error = SWFError('message')
        >>> error.message
        'message'
        >>> error.details
        ''
        >>> error = SWFError('message', 'kind')
        >>> error.message
        'message'
        >>> error.kind
        'kind'
        >>> error.details
        ''
        >>> error = SWFError('message', 'kind:')
        >>> error.message
        'message'
        >>> error.kind
        'kind'
        >>> error.details
        ''
        >>> error = SWFError('message', 'kind:details')
        >>> error.message
        'message'
        >>> error.kind
        'kind'
        >>> error.details
        'details'
        >>> error = SWFError('message', 'kind:  details ')
        >>> error.message
        'message'
        >>> error.kind
        'kind'
        >>> error.details
        'details'

        """
        Exception.__init__(self, message, *args, **kwargs)

        values = raw_error.split(':', 1)

        if len(values) == 2:
            self.details = values[1].strip()
        else:
            self.details = ''

        self.kind = values[0].strip()
        self.type_ = (self.kind.lower().strip().replace(' ', '_') if
                      self.kind else None)

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
