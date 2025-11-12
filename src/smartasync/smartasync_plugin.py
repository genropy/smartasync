"""SmartSwitch plugin for bidirectional sync/async support.

This module provides integration between SmartAsync and SmartSwitch,
allowing SmartSwitch handlers to work seamlessly in both sync and async contexts.
"""

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from smartswitch import Switcher


class SmartasyncPlugin:
    """SmartAsync plugin for SmartSwitch integration.

    This plugin enables bidirectional sync/async support for SmartSwitch handlers,
    allowing async functions to be called from both sync and async contexts without
    explicit await handling.

    Usage:
        from smartswitch import Switcher
        from smartasync import SmartasyncPlugin

        api = Switcher().plug(SmartasyncPlugin())

        @api
        async def handler():
            return "result"

        # Works in both contexts:
        result = handler()        # Sync context
        result = await handler()  # Async context

    Example with library integration:
        from smartswitch import Switcher
        from smartasync import SmartasyncPlugin

        class StorageManager:
            def __init__(self):
                self.api = Switcher(prefix='storage_').plug(SmartasyncPlugin())

            @property
            def node(self):
                @self.api
                async def _node(self, path: str):
                    # Automatically wrapped with smartasync
                    pass
                return _node

        # Standalone sync usage
        storage = StorageManager()
        node = storage.node(storage, path='file.txt')  # Works!

        # Standalone async usage
        async def main():
            storage = StorageManager()
            node = await storage.node(storage, path='file.txt')  # Also works!

    Double-wrapping Prevention:
        The plugin automatically detects if a function is already wrapped with
        @smartasync and avoids double-wrapping, making it safe to use with
        other tools like smpub that may also apply smartasync.

    Notes:
        - Requires SmartSwitch v0.5.0+ (for plugin system)
        - Only wraps async functions; sync functions pass through unchanged
        - Thread-safe and works with all SmartSwitch features
    """

    def on_decorate(self, func: Callable, switcher: "Switcher") -> None:
        """Hook called when a function is decorated (before wrapping).

        This is a notification hook. It doesn't modify the function,
        just receives notification that decoration is happening.

        Args:
            func: The function being decorated
            switcher: The Switcher instance
        """
        # No-op: we don't need to do anything on decoration
        pass

    def wrap(self, func: Callable, switcher: "Switcher") -> Callable:
        """Wrap function with smartasync if not already wrapped.

        Args:
            func: The function to potentially wrap
            switcher: The Switcher instance (unused, for protocol compatibility)

        Returns:
            The wrapped function, or original if already wrapped or sync
        """
        # Avoid double-wrapping: check if already has smartasync marker
        if hasattr(func, "_smartasync_reset_cache"):
            return func

        # Import here to avoid circular dependency
        # Only wrap async functions; let sync functions pass through
        import inspect

        from .core import smartasync
        if not inspect.iscoroutinefunction(func):
            return func

        return smartasync(func)
