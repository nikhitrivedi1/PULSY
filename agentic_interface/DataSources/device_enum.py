# Libraries
# StrEnum is a subclass of Enum that allows for string values
# Only available for Python 3.11 and above
from enum import StrEnum

class Device(StrEnum):
    OURA_RING = 'Oura Ring'
    APPLE_WATCH = 'Apple Watch'