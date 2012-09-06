nose-socket-whitelist
=====================

A `nose <http://nose.readthedocs.org/>`_ plugin that patches ``socket.getaddrinfo``
for non-local sockets, allowing you to either log all occurrences or cause the
offending test to fail.

``socketwhitelist.plugins.LoggingSocketWhitelistPlugin``
    logs the test(s) where sockets are opened, printing a summaray report to
    ``sys.stderr`` when all tests have finished executing

``socketwhitelist.plugins.ErroringSocketWhitelistPlugin``
    causes the offending test to fail with a ``SocketError``

Installation
------------

The plugin package is available from
`PyPI <http://pypi.python.org/pypi/nose-socket-whitelist/>`_ as
``nose-socket-whitelist``.

Using pip::

    pip install -U nose-socket-whitelist

or with setuptools/distribute::

    easy_install -U nose-socket-whitelist

