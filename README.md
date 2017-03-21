![Logo](docs/_static/logo.png)
## Askhome - Alexa Smart Home Skills with Python
[![Build Status](https://travis-ci.org/mathead/askhome.svg?branch=master)](https://travis-ci.org/mathead/askhome)
[![codecov](https://codecov.io/gh/mathead/askhome/branch/master/graph/badge.svg)](https://codecov.io/gh/mathead/askhome)

Askhome wraps the [Smart Home Skill API](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference) for Amazon Echo and removes all that ugly boilerplate.

Basic skill in askhome looks like this:
```python
from askhome import Smarthome, Appliance

class Star(Appliance):
    @Appliance.action
    def turn_on(self, request):
        ... # Let there be light
        
home = Smarthome()
home.add_appliance('star1', Star, name='Sun')

handler = home.lambda_handler
```

Check out the docs at http://askhome.rtfd.io!
