# How SmartAsync Works - Technical Deep Dives

This directory contains technical explanations of SmartAsync's bidirectional execution model.

## Core Concept

SmartAsync handles **four execution scenarios** with a single `@smartasync` decorator:

| Context | Method Type | Behavior | Document |
|---------|-------------|----------|----------|
| Sync → Async | `async def` | Execute with `asyncio.run()` | [sync-to-async.md](sync-to-async.md) |
| Sync → Sync | `def` | Direct pass-through | - |
| Async → Async | `async def` | Return coroutine (awaitable) | - |
| Async → Sync | `def` | Offload to thread pool | [async-to-sync.md](async-to-sync.md) |

## Available Guides

### [Sync → Async](sync-to-async.md)

**Use case**: CLI tools, scripts using modern async libraries (httpx, aiohttp).

**Topics**:
- Context detection with `asyncio.get_running_loop()`
- Execution with `asyncio.run()`
- Mermaid flow diagrams
- Performance characteristics (~100μs overhead)

### [Async → Sync](async-to-sync.md)

**Use case**: FastAPI/Django apps using legacy sync libraries (sqlite3, psycopg2).

**Topics**:
- Thread offloading with `asyncio.to_thread()`
- Why blocking I/O must not block event loop
- Mermaid sequence diagrams
- Performance characteristics (~50-100μs overhead)

---

## Implementation

SmartAsync uses Python 3.10+ **pattern matching** for clear dispatch logic:

```python
match (async_context, async_method):
    case (False, True):   # Sync → Async: asyncio.run()
    case (False, False):  # Sync → Sync: pass-through
    case (True, True):    # Async → Async: return coroutine
    case (True, False):   # Async → Sync: asyncio.to_thread()
```

## Key Design Decisions

1. **Asymmetric Caching**: Cache async context forever, always recheck sync
2. **Pattern Matching**: Clear dispatch with inline comments
3. **Thread Offloading**: Prevent event loop blocking

## Performance

| Operation | Overhead |
|-----------|----------|
| Sync → Async | ~102μs |
| Async → Async (cached) | ~1.3μs |
| Async → Sync | ~50-100μs |

**Conclusion**: Negligible for I/O operations (ms scale).

---

## Related Documentation

- [Scenarios](../scenarios/) - Real-world use cases
- [Comparison with Alternatives](../comparison-with-alternatives.md)
- [BIDIRECTIONAL-IMPLEMENTATION.md](../../BIDIRECTIONAL-IMPLEMENTATION.md)

**Last Updated**: 2025-11-10
