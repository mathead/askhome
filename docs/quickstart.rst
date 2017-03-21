Quick Start
===========

In here you'll find a fast introduction to askhome and show you how to get a simple Smart Home Skill
up and running.

Installation
------------

Install askhome with pip:

.. code-block:: console

    $ pip install git+git://github.com/mathead/askhome.git@master

If you are deploying to AWS Lambda by uploading zips, install askhome to your directory with:

.. code-block:: console

    $ pip install git+git://github.com/mathead/askhome.git@master -t /path/to/project-dir

More on :ref:`deployment <deployment>` later.

Defining Appliances
-------------------

When a `Smart Home Skill`_ is installed on Amazon Echo, Alexa first needs to discover all available
appliances with information about what *actions* they support. With askhome, you can define your
device types by subclassing :class:`Appliance <askhome.Appliance>`. Methods marked with the
:meth:`@Appliance.action <askhome.Appliance.action>` decorator will be discoverable and called when
the corresponding request comes in::

    from askhome import Appliance

    class Light(Appliance):
        @Appliance.action
        def turn_on(self, request):
            pass # Your logic for switching a light on here

        @Appliance.action
        def turn_off(self, request):
            pass # Your logic for switching a light, you guessed it, off here

Now that we've defined a light appliance type, lets fill our smart home with some::

    from askhome import Smarthome

    home = Smarthome()
    home.add_appliance('light1', Light, name='Kitchen Light',
                       description='Turn me on when cutting vegetables.')

    home.add_appliance('light2', Light, name='Bedroom Light',
                       model='Very Bright Light 8000')

We've added two lights with some additional info. For all details you can set, check the
:meth:`Smarthome.add_appliance <askhome.Smarthome.add_appliance>` method or the official
`DiscoverAppliancesResponse`_
documentation.

All that's left to do is make a handler accessible for our AWS Lambda instance (more on that in
:ref:`deployment <deployment>`)::

    handler = home.lambda_handler

And that's it! We've got a fully functioning Smart Home Skill that controls our lights. It can be
initialized with:

    "Alexa, discover my devices."

And then to control the lights:

    "Alexa, turn on the kitchen light."

Handling Requests
-----------------

When the method wrapped with :meth:`@Appliance.action <askhome.Appliance.action>` gets called, it
receives a :class:`Request <askhome.requests.Request>` object as argument. It has some basic
useful attributes such as :attr:`payload <askhome.requests.Request.payload>` or
:attr:`name <askhome.requests.Request.name>`, but what's special about it is that for every
action type a specific :class:`Request <askhome.requests.Request>` subclass is passed. These
subclasses have additional helpful attributes and a
:meth:`response <askhome.requests.Request.response>` method which simplifies the response creation.
For instance a ``set_target_temperature`` action receives a request that can do this::

    class Heater(Appliance):
        @Appliance.action
        def set_target_temperature(self, request):
            print request.temperature
            return request.response(request.temperature,
                                    mode='HEAT',
                                    previous_temperature=21.3,
                                    previous_mode='AUTO')

If the action method doesn't return anything (returns ``None``), success is implied.

Actions Overview
^^^^^^^^^^^^^^^^

Possible action methods and their corresponding ``Request`` types passed are:
    * turn_on(:class:`Request <askhome.requests.Request>`)
    * turn_off(:class:`Request <askhome.requests.Request>`)
    * set_percentage(:class:`PercentageRequest <askhome.requests.PercentageRequest>`)
    * increment_percentage(:class:`PercentageRequest <askhome.requests.PercentageRequest>`)
    * decrement_percentage(:class:`PercentageRequest <askhome.requests.PercentageRequest>`)
    * set_target_temperature(:class:`ChangeTemperatureRequest <askhome.requests.ChangeTemperatureRequest>`)
    * increment_target_temperature(:class:`ChangeTemperatureRequest <askhome.requests.ChangeTemperatureRequest>`)
    * decrement_target_temperature(:class:`ChangeTemperatureRequest <askhome.requests.ChangeTemperatureRequest>`)
    * get_target_temperature(:class:`GetTargetTemperatureRequest <askhome.requests.GetTargetTemperatureRequest>`)
    * get_temperature_reading(:class:`TemperatureReadingRequest <askhome.requests.TemperatureReadingRequest>`)
    * set_lock_state(:class:`LockStateRequest <askhome.requests.LockStateRequest>`)
    * get_lock_state(:class:`LockStateRequest <askhome.requests.LockStateRequest>`)

Here is a sample usage of all possible actions:

.. code-block:: python

    from askhome.requests import *

    class UltimateAppliance(Appliance):

        # The action_for decorator can mark a method for multiple actions
        @Appliance.action_for('turn_on', 'turn_off')
        def turn_on_off(self, request):
            # type: (Request) -> Optional[dict]
            pass # nothing special here

        @Appliance.action_for('set_percentage', 'increment_percentage',
                              'decrement_percentage')
        def control_percentage(self, request):
            # type: (PercentageRequest) -> Optional[dict]
            print request.percentage
            print request.delta_percentage

        @Appliance.action_for('set_target_temperature',
                              'increment_target_temperature',
                              'decrement_target_temperature')
        def control_temperature(self, request):
            # type: (ChangeTemperatureRequest) -> Optional[dict]
            print request.temperature
            print request.delta_temperature
            return request.response(22.8,
                                    mode='HEAT',
                                    previous_temperature=21.3,
                                    previous_mode='AUTO')

        @Appliance.action
        def get_target_temperature(self, request):
            # type: (GetTargetTemperatureRequest) -> Optional[dict]
            return request.response(21.8,
                                    cooling_temperature=20
                                    heating_temperature=23,
                                    mode='CUSTOM',
                                    mode_name='mode name')

        @Appliance.action
        def get_temperature_reading(self, request):
            # type: (TemperatureReadingRequest) -> Optional[dict]
            return request.response(21.8, timestamp=datetime.now())

        @Appliance.action_for('set_lock_state', 'get_lock_state')
        def lock_state(self, request):
            # type: (LockStateRequest) -> Optional[dict]
            return request.response('LOCKED')

For further information about these actions see the `official documentation`_.

Error Responses
^^^^^^^^^^^^^^^

If the user asked an invalid request or something goes wrong during the action execution, the Smart
Home API offers plenty of possible error responses. To respond with an error, simply raise one of
askhome's exceptions, like this::

    from askhome.exceptions import

    class Heater(Appliance):
        @Appliance.action
        def set_target_temperature(self, request):
            if request.temperature not in range(15, 25):
                raise ValueOutOfRangeError(15, 25)

All possible exceptions can be found :mod:`here <askhome.exceptions>` or at the official
`error messages`_ documentation.

.. _deployment:

Deployment
----------

Unlike the Custom Skills, Smart Home Skills have to be hosted on AWS Lambda instances.

...

Next, you can go to the official `Smart Home Skill API`_ documentation for detailed request
information or continue to :ref:`advanced-usage`.

.. links
.. _Smart Home Skill: https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/overviews/understanding-the-smart-home-skill-api
.. _DiscoverAppliancesResponse: https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#discoverappliancesresponse
.. _Smart Home Skill API: https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference
.. _official documentation: https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#message-payload
.. _error messages: https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#error-messages