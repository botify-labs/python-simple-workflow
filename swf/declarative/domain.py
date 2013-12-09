import os


# from botify.saas.backend import settings


__all__ = ['get_name', 'get_version']


def get_name():
    try:
        return os.environ.pop('WORKFLOW_DOMAIN_NAME')
    except KeyError:
        raise KeyError('domain name not found in environment '
                       'did you set WORKFLOW_DOMAIN_NAME variable ?')


def get_version():
    try:
        return os.environ.pop('WORKFLOW_DOMAIN_VERSION')
    except KeyError:
        raise KeyError('domain name not found in environment '
                       'did you set WORKFLOW_DOMAIN_VERSION variable ?')
