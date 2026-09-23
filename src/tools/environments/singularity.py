"""Singularity container execution environment backend.

Stub — singularity module was not included in the CEM888 fork.
Provides import stubs only; creating a SingularityEnvironment raises
NotImplementedError.  Full implementation can be ported from the upstream
upstream CEM888 repo if containerised execution is ever needed.
"""

import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def _get_scratch_dir() -> Path:
    """Return a directory for scratch / temporary files.

    Replicates the original's intent without requiring a Singularity
    installation or SIF cache.
    """
    return Path(tempfile.gettempdir()) / "cem888-scratch"


class SingularityEnvironment:
    """Stub that refuses to instantiate — singularity was stripped in the fork."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "Singularity container execution is not available in the CEM888 fork. "
            "Use local, docker, or ssh backends instead."
        )
