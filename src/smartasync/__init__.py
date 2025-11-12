"""SmartAsync - Unified sync/async API decorator.

Provides transparent sync/async method calling with automatic context detection.
"""

from .core import smartasync
from .smartasync_plugin import SmartasyncPlugin

__version__ = "0.3.0"
__all__ = ["smartasync", "SmartasyncPlugin"]
