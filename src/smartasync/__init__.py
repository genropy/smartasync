"""SmartAsync - Unified sync/async API decorator.

Provides transparent sync/async method calling with automatic context detection.

Recommended usage:
    import smartasync

    @smartasync.smartasync
    async def my_method(self):
        pass
"""

from .core import smartasync as smartasync

__version__ = "0.5.0"

__all__ = ["smartasync"]
