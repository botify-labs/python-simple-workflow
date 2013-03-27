# -*- coding: utf-8 -*-

from boto.exception import SWFResponseError


class CredentialsException(Exception):
    pass


def requires_connexion(fn):
    def wrapped(self):
        if not hasattr(self, '_connexion') or not self.connexion:
            err_msg = "Missing AWS credentials, please set connexion "\
                      "attribute with a valid Connexion object"
            raise CredentialsException(err_msg)

        try:
            return fn(self)
        except SWFResponseError as e:
            raise CredentialsException(e.body['message'])

    return wrapped
