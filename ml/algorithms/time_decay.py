"""Exponential time-decay utility shared by all scoring algorithms."""

import math
from datetime import datetime

from ml.config import TIME_DECAY_HALF_LIFE_DAYS

_DECAY_LAMBDA = math.log(2) / TIME_DECAY_HALF_LIFE_DAYS


def time_decay(timestamp_str: str) -> float:
    """Return exp(-λ·days_ago). Range (0, 1], approaching 0 for old events."""
    ts = datetime.fromisoformat(timestamp_str)
    days_ago = (datetime.now() - ts).total_seconds() / 86400
    return math.exp(-_DECAY_LAMBDA * days_ago)
