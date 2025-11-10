# SmartAsync - Technical Overview

**Version**: 0.1.0
**Status**: Alpha - Bidirectional implementation complete
**Python**: 3.10+ (requires pattern matching)

---

## What Is SmartAsync?

SmartAsync is a **bidirectional bridge** between sync and async Python code. It provides a single `@smartasync` decorator that makes methods work seamlessly in both synchronous and asynchronous contexts through automatic runtime detection.

**Core value**: Write code once, use it everywhere (CLI, web APIs, tests).

---

## How It Works

### Automatic Context Detection

```python
from smartasync import smartasync

@smartasync
async def fetch_data(url: str):
    async with httpx.AsyncClient() as client:
        return await client.get(url).json()

# Sync context (CLI)
data = fetch_data(url)  # No await - works!

# Async context (FastAPI)
data = await fetch_data(url)  # With await - works!
```

### Four Execution Scenarios

SmartAsync handles all combinations of context and method type:

| Execution Context | Method Type | Behavior |
|------------------|-------------|----------|
| Sync → Async | `async def` | Execute with `asyncio.run()` |
| Sync → Sync | `def` | Direct call (pass-through) |
| Async → Async | `async def` | Return coroutine (awaitable) |
| Async → Sync | `def` | Offload to thread with `asyncio.to_thread()` |

### Implementation: Pattern Matching

Uses Python 3.10+ pattern matching for clear dispatch:

```python
match (async_context, async_method):
    case (False, True):   # Sync context + Async method
        return asyncio.run(coro)

    case (False, False):  # Sync context + Sync method
        return method(*args, **kwargs)

    case (True, True):    # Async context + Async method
        return coro  # Caller must await

    case (True, False):   # Async context + Sync method
        return asyncio.to_thread(method, *args, **kwargs)
```

---

## Key Design Decisions

### 1. Asymmetric Caching

**Strategy**: Cache `True` (async context detected) forever, always recheck `False` (sync).

**Rationale**:
- Can transition sync → async (start script, then enter async context)
- Cannot transition async → sync (event loop cannot be "unwound")
- ~2μs overhead per sync call is acceptable

### 2. Pattern Matching Over Conditionals

**Choice**: `match/case` instead of nested `if/else` or dispatch table.

**Benefits**:
- Inline comments for each case
- Visual exhaustiveness (all 4 cases visible)
- Type-safe with Python 3.10+
- More maintainable

### 3. Thread Offloading for Sync-in-Async

**Choice**: `asyncio.to_thread()` instead of direct call.

**Why**: Sync blocking I/O would freeze the entire event loop. Thread offloading prevents this while maintaining simple API.

**Trade-off**: ~50-100μs overhead per call (negligible for I/O operations).

---

## Performance Characteristics

| Operation | Overhead | Impact |
|-----------|----------|--------|
| Sync → Async | ~102μs | `asyncio.run()` loop creation |
| Async → Async (cached) | ~1.3μs | Cache hit (fast path) |
| Async → Async (first) | ~2.3μs | Cache miss + detection |
| Async → Sync | ~50-100μs | Thread pool submission |

**Conclusion**: Overhead is **negligible** for typical use cases:
- Network requests: 10-200ms (overhead < 1%)
- Database queries: 1-50ms (overhead < 10%)
- File I/O: 1-100ms (overhead < 10%)

**When overhead matters**: Tight loops with thousands of calls to fast operations (<10μs).

---

## Primary Use Cases

### 1. Sync App → Async Libraries

**Problem**: CLI tools wanting to use modern async libraries (httpx, aiohttp).

**Solution**: Call async methods without `asyncio.run()` boilerplate.

```python
@smartasync
async def fetch(url: str):
    async with httpx.AsyncClient() as client:
        return await client.get(url).json()

# CLI usage - no event loop setup!
data = fetch("https://api.example.com")
```

**See**: [Scenario 01](../scenarios/01-sync-app-async-libs.md)

### 2. Async App → Sync Libraries

**Problem**: FastAPI/Django apps using legacy sync libraries (sqlite3, psycopg2).

**Solution**: Sync methods automatically offloaded to threads, event loop never blocked.

```python
@smartasync
def query_db(sql: str):
    conn = sqlite3.connect("app.db")
    # ... blocking I/O ...
    return results

@app.get("/users")
async def users():
    # Automatically threaded!
    data = await query_db("SELECT * FROM users")
    return data
```

**See**: [Scenario 02](../scenarios/02-async-app-sync-libs.md)

### 3. Unified Library API

**Problem**: Library authors maintaining separate sync and async implementations.

**Solution**: Single async implementation works for both sync and async users.

```python
class HTTPClient:
    @smartasync
    async def get(self, url: str):
        async with httpx.AsyncClient() as client:
            return await client.get(url)

# Sync users
client.get(url)

# Async users
await client.get(url)
```

**See**: [Scenario 04](../scenarios/04-unified-library-api.md)

---

## Limitations

### 1. Python 3.10+ Required

Pattern matching requires Python 3.10+.

**Mitigation**: Documented in `pyproject.toml` (`requires-python = ">=3.10"`).

### 2. Thread Pool Limits

Default thread pool has system limits (typically 5-32 threads).

**Mitigation**:
- Document in usage guides
- Users can configure `ThreadPoolExecutor` if needed
- For most cases, default is sufficient

### 3. Thread-Local State

Sync methods in async context execute in different threads.

**Implications**:
- Thread-local variables not shared across calls
- Database connections need proper management
- Transactions may require connection pooling

**Mitigation**: Document connection management patterns in scenarios.

### 4. Not Thread-Safe (by design)

Cache is per-method, not per-instance. Multiple threads accessing same instance can have race conditions.

**Mitigation**: Use per-thread instances or thread-local storage.

**See**: Thread safety guide in Scenario 01.

---

## Architecture

### Decorator Flow

```
User calls method
     ↓
Decorator wrapper invoked
     ↓
Check cache for async context
     ↓
If not cached: detect with get_running_loop()
     ↓
Pattern match (context, method_type)
     ↓
Execute appropriate strategy:
  - asyncio.run() for sync→async
  - pass-through for sync→sync
  - return coroutine for async→async
  - asyncio.to_thread() for async→sync
     ↓
Return result to user
```

### Caching Strategy

```python
_cached_has_loop = False  # Per-method closure variable

# First call in sync context
→ Check cache: False
→ Detect: get_running_loop() raises
→ Execute: asyncio.run(coro)
→ Cache stays: False

# First call in async context
→ Check cache: False
→ Detect: get_running_loop() succeeds
→ Update cache: True
→ Return: coroutine

# Subsequent calls in async context
→ Check cache: True (hit!)
→ Skip detection
→ Return: coroutine
```

---

## Testing

**Coverage**: 97% (38 statements, 1 miss)

**Test scenarios**:
- Sync context with async methods
- Async context with async methods
- Async context with sync methods (thread offloading)
- `__slots__` compatibility
- Error propagation
- Cache behavior
- Bidirectional usage

**See**: `tests/test_smartasync.py`

---

## Comparison with Alternatives

| Library | Auto-detection | Bidirectional | Dependencies | Pattern Matching |
|---------|---------------|---------------|--------------|------------------|
| **SmartAsync** | ✅ Yes | ✅ Yes | None | ✅ Yes |
| asgiref | ❌ No (2 decorators) | ✅ Yes | Yes | ❌ No |
| anyio | ❌ No | ❌ No (sync→async only) | Yes | ❌ No |
| asyncer | ❌ No (2 functions) | ✅ Yes | Yes | ❌ No |
| stdlib | N/A | ❌ No | None | N/A |

**Unique value**: Only library with automatic context detection + bidirectional support.

**See**: [Comparison with Alternatives](comparison.md)

---

## Documentation Structure

```
docs/
├── technical-overview.md         (this file)
├── comparison.md
├── how-it-works/
│   ├── sync-to-async.md         (detailed flow diagrams)
│   └── async-to-sync.md         (detailed flow diagrams)
└── ../scenarios/
    ├── 01-sync-app-async-libs.md
    ├── 02-async-app-sync-libs.md
    ├── 03-testing-async-code.md
    └── ... (more scenarios)
```

---

## Future Enhancements (Optional)

### Configuration Options
```python
@smartasync(executor=custom_executor)
def heavy_sync_method():
    ...
```

### Debug Mode
```python
@smartasync(debug=True)  # Logs execution path
async def monitored_method():
    ...
```

### Loop Reuse Patterns
Advanced patterns for WSGI middleware, batch operations.

**See**: `docs/future-enhancement-ideas/`

---

## Summary

**SmartAsync provides**:
- ✅ Automatic bidirectional sync/async bridge
- ✅ Zero configuration required
- ✅ Negligible performance overhead
- ✅ Simple, maintainable implementation
- ✅ Clear documentation and examples

**Best for**:
- CLI tools using async libraries
- Web APIs using sync legacy code
- Unified library APIs
- Testing async code without boilerplate

**Not for**:
- Multi-threaded apps with shared instances
- Tight performance loops (<10μs operations)
- Python < 3.10

---

**Project**: https://github.com/genropy/smartasync
**Documentation**: https://smartasync.readthedocs.io (planned)
**License**: MIT
