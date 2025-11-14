"""SmartSwitch plugin for bidirectional sync/async support.

This module provides integration between SmartAsync and SmartSwitch,
allowing SmartSwitch handlers to work seamlessly in both sync and async contexts.
"""

from typing import TYPE_CHECKING, Callable

from smartswitch import BasePlugin

if TYPE_CHECKING:
    from smartswitch import Switcher, MethodEntry


class SmartasyncPlugin(BasePlugin):
    """SmartAsync plugin for SmartSwitch integration.

    This plugin enables bidirectional sync/async support for SmartSwitch handlers,
    allowing async functions to be called from both sync and async contexts without
    explicit await handling.

    Usage:
        from smartswitch import Switcher
        from smartasync import SmartasyncPlugin

        api = Switcher()
        api.plug(SmartasyncPlugin)

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
                self.api = Switcher(prefix='storage_')
                self.api.plug(SmartasyncPlugin)

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
        - Requires SmartSwitch v0.6.0+ (with MethodEntry support)
        - Only wraps async functions; sync functions pass through unchanged
        - Thread-safe and works with all SmartSwitch features
    """

    def on_decore(self, switch: "Switcher", func: Callable, entry: "MethodEntry") -> None:
        """Hook called when a function is decorated.

        Mark whether this function needs smartasync wrapping.

        Args:
            switch: The Switcher instance
            func: The original function being decorated
            entry: The MethodEntry containing func and metadata
        """
        import inspect

        # Store metadata about whether to wrap
        info = entry.metadata.setdefault("smartasync", {})

        # Check if already wrapped or if it's a sync function
        if hasattr(func, "_smartasync_reset_cache"):
            info["should_wrap"] = False
        elif not inspect.iscoroutinefunction(func):
            info["should_wrap"] = False
        else:
            info["should_wrap"] = True

    def wrap_handler(self, switch: "Switcher", entry: "MethodEntry", call_next: Callable) -> Callable:
        """Wrap handler with smartasync if needed.

        Args:
            switch: The Switcher instance
            entry: The MethodEntry containing func and metadata
            call_next: The next handler in the chain

        Returns:
            Wrapped handler if async, otherwise pass-through
        """
        # Check if we should wrap
        info = entry.metadata.get("smartasync", {})
        if not info.get("should_wrap", False):
            return call_next

        # Wrap with smartasync once
        from .core import smartasync
        return smartasync(call_next)
