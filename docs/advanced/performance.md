# Performance

Understanding SmartAsync's performance characteristics.

## Overhead by Scenario

| Scenario | Overhead | Impact |
|----------|----------|--------|
| Sync → Async | ~102μs | `asyncio.run()` loop creation |
| Async → Async (cached) | ~1.3μs | Negligible |
| Async → Async (first call) | ~2.3μs | Context detection |
| Async → Sync | ~50-100μs | Thread pool offloading |

## Real-World Impact

For typical I/O operations, SmartAsync overhead is **negligible**:

### Network Requests
- Request time: 10-200ms
- SmartAsync overhead: ~0.1ms
- **Impact: < 1%**

### Database Queries
- Query time: 1-50ms
- SmartAsync overhead: ~0.1ms
- **Impact: < 10%**

### File I/O
- Operation time: 1-100ms
- SmartAsync overhead: ~0.1ms
- **Impact: < 10%**

## When Overhead Matters

SmartAsync may not be suitable for:

- **Tight loops** with thousands of calls
- **Fast operations** (<10μs) called repeatedly
- **Performance-critical hot paths**

In these cases, consider using explicit async/await or refactoring to batch operations.

## Optimization Tips

### 1. Batch Operations

Instead of:
```python
for item in items:
    result = await process(item)  # Many calls
```

Do:
```python
results = await asyncio.gather(
    *[process(item) for item in items]
)
```

### 2. Cache Results

If calling same method repeatedly:
```python
@functools.cache
@smartasync
async def expensive_operation():
    ...
```

### 3. Use Async Context When Possible

Async context has lower overhead (~1-2μs vs ~100μs).

## Benchmarking

To benchmark SmartAsync in your application:

```python
import time

# Measure sync context
start = time.perf_counter()
result = obj.method()
sync_time = time.perf_counter() - start

# Measure async context  
async def bench():
    start = time.perf_counter()
    result = await obj.method()
    return time.perf_counter() - start

async_time = asyncio.run(bench())

print(f"Sync: {sync_time*1000:.2f}ms")
print(f"Async: {async_time*1000:.2f}ms")
```

## See Also

- [Technical Overview →](technical-overview.md)
- [How It Works →](../how-it-works/index.md)
