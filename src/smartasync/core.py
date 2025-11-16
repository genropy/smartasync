"""SmartAsync - Unified sync/async API decorator.

Automatic context detection for methods that work in both sync and async contexts.
"""

import asyncio
import functools


def wrapper(method):
    """
    Create a bidirectional wrapper for a method or function.

    This is the core wrapping logic used by the smartasync decorator
    and can be used standalone for runtime wrapping.

    Works with:
    - Bound methods (automatically includes self)
    - Unbound functions (no self parameter)

    Args:
        method: Method or function to wrap (async or sync)

    Returns:
        Wrapped function that works in both sync and async contexts

    Example:
        # Standalone usage for runtime wrapping
        def my_function(x: int) -> int:
            return x * 2

        wrapped = wrapper(my_function)
        result = wrapped(5)  # Works in both sync and async contexts
    """
    # Import time: Detect if method is async
    is_coro = asyncio.iscoroutinefunction(method)

    # Asymmetric cache: only cache True (async context found)
    _cached_has_loop = False

    @functools.wraps(method)
    def _wrapper(*args, **kwargs):
        """Generic wrapper - works with bound methods and functions."""
        nonlocal _cached_has_loop

        # Context detection with asymmetric caching
        if _cached_has_loop:
            async_context = True
        else:
            try:
                asyncio.get_running_loop()
                # Found event loop! Cache it forever
                async_context = True
                _cached_has_loop = True
            except RuntimeError:
                # No event loop - sync context
                # Don't cache False, always re-check next time
                async_context = False

        async_method = is_coro

        # Dispatch based on (async_context, async_method) using pattern matching
        match (async_context, async_method):
            case (False, True):
                # Sync context + Async method → Run with asyncio.run()
                coro = method(*args, **kwargs)
                try:
                    return asyncio.run(coro)
                except RuntimeError as e:
                    if "cannot be called from a running event loop" in str(e):
                        raise RuntimeError(
                            f"Cannot call {method.__name__}() synchronously from within "
                            f"an async context. Use 'await {method.__name__}()' instead."
                        ) from e
                    raise

            case (False, False):
                # Sync context + Sync method → Direct call (pass-through)
                return method(*args, **kwargs)

            case (True, True):
                # Async context + Async method → Return coroutine to be awaited
                return method(*args, **kwargs)

            case (True, False):
                # Async context + Sync method → Offload to thread (don't block event loop)
                return asyncio.to_thread(method, *args, **kwargs)

    # Add cache reset method for testing
    def reset_cache():
        nonlocal _cached_has_loop
        _cached_has_loop = False

    _wrapper._smartasync_reset_cache = reset_cache

    return _wrapper


def smartasync(method):
    """Bidirectional decorator for methods that work in both sync and async contexts.

    Automatically detects whether the code is running in an async or sync
    context and adapts accordingly. Works in BOTH directions:
    - Async methods called from sync context (uses asyncio.run)
    - Sync methods called from async context (uses asyncio.to_thread)

    Features:
    - Auto-detection of sync/async context using asyncio.get_running_loop()
    - Asymmetric caching: caches True (async), always checks False (sync)
    - Enhanced error handling with clear messages
    - Works with both async and sync methods/functions
    - No configuration needed - just apply the decorator
    - Prevents blocking event loop when calling sync methods from async context

    How it works:
    - At import time: Checks if method is async using asyncio.iscoroutinefunction()
    - At runtime: Detects if running in async context (checks for event loop)
    - Asymmetric cache: Once async context is detected (True), it's cached forever
    - Sync context (False) is never cached, always re-checked
    - This allows transitioning from sync → async, but not async → sync (which is correct)
    - Uses pattern matching to dispatch based on (has_loop, is_coroutine)

    Execution scenarios (async_context, async_method):
    - (False, True):  Sync context + Async method → Execute with asyncio.run()
    - (False, False): Sync context + Sync method → Direct call (pass-through)
    - (True, True):   Async context + Async method → Return coroutine (for await)
    - (True, False):  Async context + Sync method → Offload to thread (asyncio.to_thread)

    Args:
        method: Method or function to decorate (async or sync)

    Returns:
        Wrapped function that works in both sync and async contexts

    Example:
        class Manager:
            @smartasync
            async def async_configure(self, config: dict) -> None:
                # Async implementation uses await
                await self._async_setup(config)

            @smartasync
            def sync_process(self, data: str) -> str:
                # Sync implementation (e.g., CPU-bound or legacy code)
                return process_legacy(data)

        # Sync context usage
        manager = Manager()
        manager.async_configure({...})  # No await needed! Uses asyncio.run()
        result = manager.sync_process("data")  # Direct call

        # Async context usage
        async def main():
            manager = Manager()
            await manager.async_configure({...})  # Normal await
            result = await manager.sync_process("data")  # Offloaded to thread!

    Note:
        This decorator now uses the wrapper() function internally.
        For runtime wrapping, use wrapper() directly instead of this decorator.
    """
    return wrapper(method)
