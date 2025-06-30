from importlib.util import find_spec

from .maimai import MaimaiAreas, MaimaiClient, MaimaiClientMultithreading, MaimaiItems, MaimaiPlates, MaimaiScores, MaimaiSongs
from .models import *
from .providers import *

if find_spec("fastapi"):
    from .api import MaimaiRoutes
