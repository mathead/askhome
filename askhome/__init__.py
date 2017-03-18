import logging

# Initialize logger that is used in other modules
logger = logging.getLogger('askhome')
logger.addHandler(logging.StreamHandler())

from .appliance import Appliance
from .smarthome import Smarthome
from .requests import create_request
