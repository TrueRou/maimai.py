from importlib.util import find_spec

from .maimai import *
from .models import *
from .providers import *

if find_spec("fastapi"):
    from .api import MaimaiRoutes as MaimaiRoutes
