"""SmartAsync - Unified sync/async API decorator.

Provides transparent sync/async method calling with automatic context detection.
"""

from .core import SmartAsync, smartasync

__version__ = "0.1.0"
__all__ = ["SmartAsync", "smartasync"]
