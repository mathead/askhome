.. _advanced-usage:

Advanced Usage
==============

This section covers some more advanced features of askhome.

Reusing Appliance Details
-------------------------

If you're creating a Smart Home Skill for devices from one manufacturer, you probably don't want to
repeat yourself when specifying the details when adding the device with
:meth:`Smarthome.add_appliance <askhome.Smarthome.add_appliance>`. You can set defaults to either
:class:`Appliance <askhome.Appliance>` or all devices in the :class:`Smarthome <askhome.Smarthome>`
like this::

    class Door(Appliance):
        class Details:
            model = 'QualityDoor'
            version = '2.0'

    home = Smarthome(manufacturer='EvilCorp')
    home.add_appliance('door1', Door, name='Front Door')
    home.add_appliance('door2', Door, name='Back Door', version='1.0')

Resulting detail value is resolved in this order:
    #. :meth:`Smarthome.add_appliance <askhome.Smarthome.add_appliance>` keyword arguments
    #. :class:`Appliance.Details <askhome.Appliance.Details>` inner class
    #. :meth:`Smarthome.__init__ <askhome.Smarthome.__init__>` keyword arguments

Smarthome Handlers
------------------

The simple skill described in :ref:`quick-start` has a potential problem in that it needs to know
all appliances user has on every request. For example, if you keep the data in a remote database,
it's wasteful to query for every appliance when switching one light on.

This problem can be solved by handling discovery and getting appliances for requests manually::

    home = Smarthome()

    @home.discover_handler
    def discover(request):
        # Query the database here for all available appliances
        home.add_appliance('light1', Light, name='Kitchen Light',
                           additional_details={'type': 'Light'})
        return request.response(home)

    @home.get_appliance_handler
    def get_appliance(request):
        if request.appliance_details['type'] == 'Light':
            return Light

Here we've used the `additional_details`_ field the Smart Home API offers. You can save custom data
in there during discovery and for every subsequent request you get that data back. This way, we
query the database only once during discovery.

User Data
^^^^^^^^^

Often you will still need to query for some information about the user that sent the request. For
that, there is another :class:`Smarthome <askhome.Smarthome>` decorator::

    @home.prepare_request_handler
    def prepare_request(request):
        # Query the database for ip address of the user
        ip = '1.2.3.4'
        request.custom_data = {'user_ip': ip}

The above ``prepare_request`` function gets called before every request is processed. We save our
user data to :attr:`Request.custom_data <askhome.requests.Request.custom_data>` attribute, which we
can use in any of our action methods.

.. links
.. _additional_details: https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#payload-1
