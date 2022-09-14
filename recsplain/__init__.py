__version__="0.0.8"
from .strategies import BaseStrategy, AvgUserStrategy, RedisStrategy
from .encoders import PartitionSchema
from .endpoint import run_server
