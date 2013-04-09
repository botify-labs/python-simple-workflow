.. _quickstart:

==========
Quickstart
==========


.. _installation:

Installation
============

.. code-block:: bash

	python setup.py install

.. _usage:

Usage
=====

Before you ask
--------------

To be usable, the python simple workflow package modules have to be aware of your AWS credentials.To do so, python-simple-workflow provides a ``set_aws_credentials`` helper function.

.. code-block:: python

	>>> from swf.core import set_aws_credentials
	>>> set_aws_credentials('MYAWSACCESSKEYID', 'MYAWSSECRETACCESSKEY')

	# And then you're good to go...
	>>> queryset = DomainQuery()
	>>> queryset.all()
	[Domain('test1'), Domain('test2')]