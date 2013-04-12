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


Models
------

Simple Workflow concepts are to be manipulated through python-simple-workflow using models. They look
quite the same django's model, and are there to help representing amazon simple workflow concepts as
objects.

A good walkthrough example worths it all. For more details about models, see `python-simple-workflow api documentation <https://python-simple-workflow.readthedocs.org/en/latest/api.html>`_ .

.. code-block:: python

    # Models resides in swf.models module
    >>> from swf.models import Domain, WorkflowType, WorkflowExecution, ActivityType, Event, History

    # Once imported you're ready to create a model instance, let's say,
    # a domain for example.
    >>> D = Domain(
        "my-test-domain-name",
        description="my-test-domain-description",
        retention_period=60
    )

    # Now, a Domain model instance has been created, but just as in Django,
    # it's totally local, nothing has been sent to amazon swf. If we want to,
    # let's just save it
    >>> D.save()

    # Okay, now, if no errors happened, this should be saved amazon-side,
    # need a proof? exists method let you know if the model your manipulating
    # has an upstream version
    >>> D.exists
    True

    # So now we've got a model existing both locally and remotly, but if whatever
    # changes are made to the object, how to ensure local and remote models are still synced
    # and which changes have been maid you must ask yourself.
    >>> D.is_synced
    True
    >>> D.changes
    []
    >>> D.name = "My Brand New Shinny Name"  # Let's update one of our domain attribute
    >>> D.is_synced  # local and remote model representation are now out of sync
    False

    # .changes models method lets you know what exactly are the changes between
    # local and remote versions
    >>> D.changes
    [
        Diff(
            attribute='name',
            local_value='My Brand New Shinny Name',
            remote_value='my-test-domain-name'
        ),
    ]


QuerySets
---------

Models can be retrieved and instantiated via querysets. To continue over the django comparison,
they're behaving like django managers.

.. code-block:: python

    # As querying for models needs a valid connection to amazon service,
    # Queryset objects cannot act as classmethods proxy and have to be instantiated;
    # most of the time against a Domain model instance
    >>> from swf.querysets import DomainQuerySet, WorkflowTypeQuerySet

    # Domain querysets can be instantiated directly
    >>> domain_qs = DomainQuerySet()
    >>> workflow_domain = domain_qs.get("MyTestDomain")  # and specific model retieved via .get method
    >>> workflow_qs = WorkflowTypeQuerySet(workflow_domain)  # queryset built against model instance example

    >>> workflow_qs.all()
    [WorkflowType("TestType1"), WorkflowType("TestType2"),]

    >>> workflow_qs.filter(status=DEPRECATED)
    [WorkflowType("DeprecatedType1"),]