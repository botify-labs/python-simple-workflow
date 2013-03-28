======================
Python Simple Workflow
======================

*Under heavy development, and not yet usable*

python-simple-workflow is a wrapper for `Amazon Simple Workflow <http://aws.amazon.com/en/swf/>`_ service. It aims to provide
some abstractions over `Boto <https://boto.readthedocs.org/en/latest/ref/swf.html>`_ library SWF API implementation, like querysets and objects over
commonly used concepts: Domains, Workflows, Activities, and so on.

It is under MIT license, and any ideas, features requests, patches, pull requests to improve it are of course welcome.

Installation
============

.. code-block:: shell

    python setup.py install


Usage
=====


Before you ask
--------------

To be usable, the python simple workflow package modules have to be aware of your AWS credentials. To do so,
python-simple-workflow provides a ``set_aws_credentials`` helper function.

.. code-block:: shell

    >>> from swf.core import set_aws_credentials
    >>> set_aws_credentials('MYAWSACCESSKEYID', 'MYAWSSECRETACCESSKEY')

    # And then you're good to go...
    >>> queryset = DomainQuery()
    >>> queryset.all()
    [Domain('test1'), Domain('test2')]

