# -*- coding: utf-8 -*-

from boto.exception import SWFResponseError


class CredentialsException(Exception):
    pass


def requires_connexion(fn):
    """Ensures decorated method obect's exposes a valid connexion object

    Any object pretending to talk with amazon simple workflow webservice
    should expose a valid `connexion` attribute. See swf.base.Connexion.

    This decorator will also ensure that credentials are valid, and
    will raise a CredentialsException with a plain error message when
    it's not the case.
    """
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
