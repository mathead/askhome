Welcome to Askhome!
===================

Askhome wraps the Smart Home Skill API for Amazon Echo and removes all that ugly boilerplate.

Basic skill in askhome looks like this::

    from askhome import Smarthome, Appliance

    class Star(Appliance):
        @Appliance.action
        def turn_on(self, request):
            ... # Let there be light

    home = Smarthome()
    home.add_device('star1', Star, name='Sun')

    handler = home.lambda_handler

Features
--------

a

User Guide
----------

.. toctree::
    :maxdepth: 2

    quickstart
    advanced

API Documentation
-----------------

If you are looking for information on a specific function, class or method, this part of the
documentation is for you.

.. toctree::
    :maxdepth: 2

    api