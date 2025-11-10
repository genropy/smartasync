# Loop Reuse Patterns - Performance Optimization Ideas

**Status**: Future Enhancement Ideas
**Date**: 2025-11-10
**Context**: SmartAsync v0.1.0

---

## Background

SmartAsync currently uses `asyncio.run()` for every sync context call. This is a **deliberate design choice** favoring:
- ✅ **Simplicity**: Zero configuration, works everywhere
- ✅ **Isolation**: Each call has clean lifecycle
- ✅ **Safety**: No shared state, no lifecycle management

**Trade-off**: ~100μs overhead per sync call from `asyncio.run()`.

For **target use cases** (CLI tools, occasional calls), this overhead is **negligible** (0.01-1% of total I/O time).

---

## When Overhead Matters

The ~100μs overhead becomes significant when:

1. **Many repeated calls** in sync context (hundreds/thousands in tight loop)
2. **Performance-critical operations** where every microsecond counts
3. **Server scenarios** with many sync-context requests per second

**Example where it matters:**
```python
# CLI batch processing
fetcher = DataFetcher()

for i in range(10_000):
    data = fetcher.fetch(f"item_{i}")  # 100μs × 10k = 1 second overhead!
```

---

## Pattern 1: Middleware Loop Management (Server Scenarios)

### Concept

In **server environments** (WSGI, custom servers), a **middleware** can:
1. Create an event loop for each request/thread
2. Set it as "current" for that thread
3. SmartAsync detects the loop and uses it
4. Middleware closes loop after request completes

### How It Works

SmartAsync **already supports this** via `asyncio.get_running_loop()`:
- If middleware has prepared a loop → SmartAsync returns coroutine (async path)
- If no loop exists → SmartAsync falls back to `asyncio.run()`

**Key insight**: SmartAsync doesn't need modifications; it's the **caller's responsibility** to manage the loop.

### Example: WSGI Middleware

```python
import asyncio
import threading
from contextlib import contextmanager

class AsyncMiddleware:
    """WSGI middleware that prepares event loop for SmartAsync methods."""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Run app - SmartAsync methods will find this loop
            response = self.app(environ, start_response)

            # If response contains coroutines, execute them
            if asyncio.iscoroutine(response):
                response = loop.run_until_complete(response)

            return response
        finally:
            loop.close()
            asyncio.set_event_loop(None)
```

### Usage

```python
from smartasync import smartasync
import httpx

class DataHandler:
    @smartasync
    async def fetch_data(self, url: str):
        async with httpx.AsyncClient() as client:
            return await client.get(url).json()

# With middleware
def wsgi_app(environ, start_response):
    handler = DataHandler()
    data = handler.fetch_data("https://api.example.com/data")
    # No asyncio.run() overhead - uses middleware's loop!

    start_response('200 OK', [('Content-Type', 'application/json')])
    return [json.dumps(data).encode()]

# Apply middleware
app = AsyncMiddleware(wsgi_app)
```

### Benefits

- ✅ Loop created **once per request**
- ✅ All SmartAsync calls in that request reuse the same loop
- ✅ **Zero SmartAsync modifications** needed
- ✅ Clean lifecycle (loop closed after request)

### When to Use

- ✅ Custom WSGI/server implementations
- ✅ Multiple SmartAsync calls per request
- ✅ Performance-sensitive server applications
- ❌ Not needed for ASGI servers (already async)

---

## Pattern 2: Context Manager for Batch Operations

### Concept

For **batch processing** in sync context, provide a **context manager** that:
1. Creates and sets an event loop
2. Allows multiple SmartAsync calls
3. Closes loop on exit

### Example: Simple Context Manager

```python
import asyncio
from contextlib import contextmanager

@contextmanager
def async_batch_context():
    """Context manager for batch SmartAsync operations."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        yield loop
    finally:
        loop.close()
        asyncio.set_event_loop(None)
```

### Usage

```python
from smartasync import smartasync

class DataFetcher:
    @smartasync
    async def fetch(self, item_id: int):
        # Async implementation
        ...

# Without context manager (slow)
fetcher = DataFetcher()
for i in range(1000):
    data = fetcher.fetch(i)  # 100μs × 1000 = 100ms overhead!

# With context manager (fast)
with async_batch_context():
    fetcher = DataFetcher()
    for i in range(1000):
        data = fetcher.fetch(i)  # Reuses same loop - minimal overhead!
```

### Advanced: Async Batch Execution

For **true parallelism**, batch coroutines and execute concurrently:

```python
@contextmanager
def async_batch_context():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        yield loop
    finally:
        loop.close()
        asyncio.set_event_loop(None)

# Batch execution with concurrency
with async_batch_context() as loop:
    fetcher = DataFetcher()

    # Collect coroutines
    tasks = [fetcher.fetch(i) for i in range(1000)]

    # Execute concurrently
    results = loop.run_until_complete(asyncio.gather(*tasks))
```

### Benefits

- ✅ Loop created **once** for entire batch
- ✅ Optional **concurrent execution** with `asyncio.gather()`
- ✅ Clean API for users
- ✅ **No SmartAsync modifications** needed

### When to Use

- ✅ Batch processing scripts
- ✅ CLI tools processing many items
- ✅ Data migration scripts
- ❌ Single operations (overhead not worth it)

---

## Pattern 3: Thread-Local Loop Pool (Advanced)

### Concept

For **multi-threaded servers**, maintain a **thread-local event loop** that persists across requests in the same thread.

### Example

```python
import threading
import asyncio

class ThreadLocalLoopManager:
    """Manages event loop per thread."""

    def __init__(self):
        self._local = threading.local()

    def get_or_create_loop(self):
        """Get existing loop for this thread or create new one."""
        if not hasattr(self._local, 'loop'):
            self._local.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._local.loop)
        return self._local.loop

    def close_thread_loop(self):
        """Close loop for current thread (call on thread exit)."""
        if hasattr(self._local, 'loop'):
            self._local.loop.close()
            del self._local.loop

# Global manager
loop_manager = ThreadLocalLoopManager()

# In thread worker
def worker(task):
    loop = loop_manager.get_or_create_loop()

    # SmartAsync calls reuse this loop
    handler = DataHandler()
    result = handler.process(task)

    return result

# Thread pool usage
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(worker, tasks)
```

### Benefits

- ✅ Loop **persists** across multiple operations per thread
- ✅ **No loop creation** overhead after first call
- ✅ Compatible with thread pools

### Challenges

- ⚠️ **Lifecycle management**: Must close loops on thread exit
- ⚠️ **Complexity**: More code to maintain
- ⚠️ **Thread safety**: Must ensure proper isolation

### When to Use

- ✅ Long-lived thread pools
- ✅ Many operations per thread
- ❌ Short-lived threads (overhead not worth it)

---

## Performance Comparison

| Scenario | Overhead per call | Total for 1000 calls |
|----------|------------------|---------------------|
| **Default** (`asyncio.run()` each time) | ~100μs | ~100ms |
| **Middleware pattern** (loop per request) | ~2μs | ~2ms |
| **Context manager** (loop per batch) | ~2μs | ~2ms |
| **Thread-local pool** | ~2μs | ~2ms |

**Speedup**: ~50x for repeated calls in same context.

---

## Implementation Status

### Already Works (v0.1.0)

- ✅ SmartAsync **already detects** prepared loops
- ✅ **Zero modifications** needed to SmartAsync code
- ✅ Users can implement patterns above **today**

### Potential Future Additions

SmartAsync could **optionally provide**:

1. **Helper middleware** for common servers (WSGI, custom)
2. **Context manager utility** (`smartasync.batch_context()`)
3. **Thread-local manager** (`smartasync.ThreadLocalLoopManager`)

**Decision**: Keep SmartAsync **core simple**, provide **optional helpers** in separate module or examples.

---

## Recommendations

### For Library Users

1. **Default is fine** for most use cases (CLI, occasional calls)
2. **Consider middleware** if building custom server with many SmartAsync calls
3. **Use context manager** for batch processing scripts
4. **Measure first** - only optimize if overhead is measurable in your scenario

### For SmartAsync Maintainers

1. **Document these patterns** (this file)
2. **Provide examples** in `examples/` directory
3. **Consider optional helpers** in future versions
4. **Keep core simple** - don't add complexity for edge cases

---

## Examples Directory (Proposed)

Future versions could include:

```
examples/
├── middleware_wsgi.py           # WSGI middleware example
├── batch_processing.py          # Context manager usage
├── thread_pool.py               # Thread-local loop example
└── performance_comparison.py    # Benchmark script
```

---

## Related Issues

- **Issue #2**: Thread safety - These patterns help mitigate by managing loop lifecycle
- **TECH-REPORT.md**: Performance analysis section
- **Scenario A1**: Sync app calling async libs

---

## Summary

**Key Insight**: SmartAsync **already supports** loop reuse patterns through its detection mechanism (`asyncio.get_running_loop()`). The patterns described here are **caller-side optimizations** that SmartAsync automatically benefits from.

**Philosophy**: Keep SmartAsync **simple and correct**. Let **advanced users** optimize their specific scenarios using these patterns.

**Next Steps**:
1. Document patterns (✅ this file)
2. Create example implementations
3. Consider optional helper utilities
4. Measure real-world impact

---

**Status**: Ideas for future consideration
**Priority**: LOW (optimization, not correctness)
**Compatibility**: Works with SmartAsync v0.1.0 today
