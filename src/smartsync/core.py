"""SmartSync - Unified sync/async API decorator.

Standalone version for testing outside of genro-storage context.
"""

import asyncio
import functools
from typing import Callable, TypeVar, Any

T = TypeVar('T')


class SmartSync:
    """Base class for unified sync/async API.

    Provides a single slot '_sync_mode' that controls whether async methods
    are wrapped with asyncio.run() or return coroutines.

    Features:
    - Works with regular classes and __slots__
    - No global registry, no weakref, no cleanup needed
    - Minimal memory overhead (one slot per instance)
    - Clean inheritance pattern

    Usage:
        from smartsync import SmartSync, smartsync

        class MyClass(SmartSync):
            def __init__(self, _sync: bool = False):
                SmartSync.__init__(self, _sync)

            @smartsync
            async def my_method(self):
                await asyncio.sleep(0.1)
                return "result"

        # Sync mode
        obj_sync = MyClass(_sync=True)
        result = obj_sync.my_method()  # No await needed!

        # Async mode
        obj_async = MyClass(_sync=False)
        result = await obj_async.my_method()  # Await required

    With __slots__:
        class MyClass(SmartSync):
            __slots__ = ('data',)  # NO __weakref__ needed!

            def __init__(self, _sync: bool = False):
                SmartSync.__init__(self, _sync)
                self.data = []

            @smartsync
            async def process(self):
                ...
    """
    __slots__ = ('_sync_mode',)

    def __init__(self, _sync: bool = False):
        """Initialize sync mode.

        Args:
            _sync: If True, async methods decorated with @smartsync
                   are wrapped with asyncio.run() and can be called
                   without await. If False (default), methods return
                   coroutines that must be awaited.
        """
        self._sync_mode = _sync


def smartsync(method):
    """Decorator for methods that work in both sync and async contexts.

    Automatically detects whether the code is running in an async or sync
    context and adapts accordingly.

    Features:
    - Auto-detection of sync/async context using asyncio.get_running_loop()
    - Asymmetric caching: caches True (async), always checks False (sync)
    - Enhanced error handling with clear messages
    - Works with both async and sync methods (sync methods are passed through)
    - No configuration needed - just apply the decorator

    How it works:
    - At import time: Checks if method is async using asyncio.iscoroutinefunction()
    - At runtime: Detects if running in async context (checks for event loop)
    - Asymmetric cache: Once async context is detected (True), it's cached forever
    - Sync context (False) is never cached, always re-checked
    - This allows transitioning from sync → async, but not async → sync (which is correct)

    Args:
        method: Method to decorate (async or sync)

    Returns:
        Wrapped function that works in both sync and async contexts

    Example:
        class Manager:
            @smartsync
            async def configure(self, config: dict) -> None:
                # Implementation uses await
                await self._setup(config)

        # Sync usage - auto-detected
        manager = Manager()
        manager.configure({...})  # No await needed!

        # Async usage - auto-detected
        async def main():
            manager = Manager()
            await manager.configure({...})  # Await required
    """
    # Import time: Detect if method is async
    if asyncio.iscoroutinefunction(method):
        # Asymmetric cache: only cache True (async context found)
        _cached_has_loop = False

        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            nonlocal _cached_has_loop

            coro = method(self, *args, **kwargs)

            # If cache says True, use it (we're in async context)
            if _cached_has_loop:
                return coro

            # Otherwise, check current context
            try:
                asyncio.get_running_loop()
                # Found event loop! Cache it forever
                _cached_has_loop = True
                return coro
            except RuntimeError:
                # No event loop - sync context, execute with asyncio.run()
                # Don't cache False, always re-check next time
                try:
                    return asyncio.run(coro)
                except RuntimeError as e:
                    if "cannot be called from a running event loop" in str(e):
                        raise RuntimeError(
                            f"Cannot call {method.__name__}() synchronously from within "
                            f"an async context. Use 'await {method.__name__}()' instead."
                        ) from e
                    raise

        # Add cache reset method for testing
        def reset_cache():
            nonlocal _cached_has_loop
            _cached_has_loop = False

        wrapper._smartsync_reset_cache = reset_cache

        return wrapper
    else:
        # Sync method - no wrapping needed
        return method
