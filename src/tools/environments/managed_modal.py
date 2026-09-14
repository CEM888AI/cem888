"""Managed Modal (CEM888.AI Tool Gateway) execution environment.

Stub — managed_modal backend was not included in the CEM888 fork.
Provides import stubs only; creating a ManagedModalEnvironment raises
NotImplementedError.
"""

import logging

logger = logging.getLogger(__name__)


class ManagedModalEnvironment:
    """Stub — managed modal execution is not available in the CEM888 fork."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "Managed Modal execution (CEM888.AI Tool Gateway) is not "
            "available in the CEM888 fork. Use local, ssh, or docker "
            "backends instead."
        )
