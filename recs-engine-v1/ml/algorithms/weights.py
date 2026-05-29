"""Adaptive hybrid weight schedule (content / collab / popularity)."""

from ml.config import (
    COLD_CONTENT_BASE, COLD_COLLAB_BASE,
    CONTENT_GROWTH, COLLAB_GROWTH,
    MAX_CONTENT_WEIGHT, MAX_COLLAB_WEIGHT,
)


def hybrid_weights(n_interacted: int) -> tuple[float, float, float]:
    """
    Returns (content_w, collab_w, popularity_w) that always sum to 1.0.

    Weights grow linearly with interaction count and are capped at config maxima.
      n=0  (cold start): content=0.30, collab=0.10, pop=0.60
      n=25+ (warm user): content=0.50, collab=0.18, pop=0.32
    """
    content_w = min(MAX_CONTENT_WEIGHT, COLD_CONTENT_BASE + n_interacted * CONTENT_GROWTH)
    collab_w  = min(MAX_COLLAB_WEIGHT,  COLD_COLLAB_BASE  + n_interacted * COLLAB_GROWTH)
    pop_w     = 1.0 - content_w - collab_w
    return content_w, collab_w, pop_w
