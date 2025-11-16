"""SmartAsync - Unified sync/async API decorator.

Provides transparent sync/async method calling with automatic context detection.
"""

from .core import smartasync, wrapper

__version__ = "0.4.0"
__all__ = ["smartasync", "wrapper"]
