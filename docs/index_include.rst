.. module:: score.uws
.. role:: confkey
.. role:: confdefault

*********
score.uws
*********

Module integrating uwebsockets_ into your :ref:`SCORE <index>` application.

.. _uwebsockets: https://github.com/uNetworking/uWebSockets

Installation
============

This package was written to work with libuv_, it needs to compile its own
version of the uws library. So you will first need to install the development
package for libuv and cython:

.. code-block:: console

    $ sudo apt install libuv1-dev
    $ pip install cython

After that, you can just checkout the desired version and build/install the
python package manually using pip:

.. code-block:: console

    $ git clone --recurse-submodules https://github.com/score-framework/py.uws score.uws
    $ pip install score.uws

.. _libuv: https://github.com/libuv/libuv


Quickstart
==========

Just create an instance of the :class:`UwsWorker` and add your hooks:

.. code-block:: python

    from score.uws import UwsWorker

    class PolitePingServer(UwsWorker):

        def prepare(self):
            super().prepare()
            self.hub.add_connect_callback(self.on_connect)
            self.hub.add_message_callback(self.on_message)

        def on_connect(self, client):
            client.send('Hello!')

        def on_message(self, client, message):
            client.send(message)

You can store state information on the client object's :attr:`data
<Client.data>` `dict`:

.. code-block:: python

    from score.uws import UwsWorker

    class RudePingServer(UwsWorker):

        def prepare(self):
            super().prepare()
            self.hub.add_connect_callback(self.on_connect)
            self.hub.add_message_callback(self.on_message)

        def on_connect(self, client):
            client.data['counter'] = 0

        def on_message(self, client, message):
            client.send(message)
            client.data['counter'] += 1
            if client.data['counter'] >= 3:
                client.send('Enough! Go bother someone else!')
                client.disconnect()

Afterwards, you can export this worker from your module and update your
:mod:`score.serve` configuration to include your module:

.. code-block:: python

    class ConfiguredMyApplication(ConfiguredModule):

        # ...

        def score_serve_workers(self):
            return PolitePingServer(self.ws)

.. code-block:: ini

    [score.init]
    modules =
        score.ws  # note: score.ws, not uws!
        myapplication

    [serve]
    modules =
        myapplication


API
===

.. autoclass:: Hub
    :members:

.. autoclass:: Client
    :members:

    .. attribute:: hub

        The :class:`Hub` this client belongs to.

    .. attribute:: data

        A `dict` that can be used by your applicat6ion to store
        connection-specific information.
