# SmartAsync - Common Patterns

Patterns extracted from test suite (tests/test_smartasync.py) showing proven usage.

## Pattern 1: Async Method in Sync Context
**Frequency**: 5+ tests
**Use case**: CLI tools, scripts calling async libraries

```python
# From: tests/test_smartasync.py::test_sync_context
class Manager:
    @smartasync
    async def fetch_data(self, url: str) -> dict:
        async with httpx.AsyncClient() as client:
            return await client.get(url).json()

# Sync usage - no asyncio.run() needed
manager = Manager()
data = manager.fetch_data("https://api.example.com")
```

**Key points**:
- No `await` keyword in sync context
- No manual `asyncio.run()` needed
- Returns actual result, not coroutine
- ~102μs overhead per call

## Pattern 2: Sync Method in Async Context
**Frequency**: 2+ tests
**Use case**: Async apps using legacy sync libraries

```python
# From: tests/test_smartasync.py::test_bidirectional_scenario_a2
class LegacyDatabase:
    @smartasync
    def query(self, sql: str) -> list:
        # Blocking sync code (e.g., sqlite3)
        conn = sqlite3.connect("db.sqlite")
        return conn.execute(sql).fetchall()

# Async usage - auto-threaded
async def handler():
    db = LegacyDatabase()
    results = await db.query("SELECT * FROM users")
    # Event loop not blocked!
```

**Key points**:
- Must `await` in async context
- Automatically offloaded to thread pool
- Prevents blocking event loop
- ~50-100μs overhead per call

## Pattern 3: Concurrent Sync Operations in Async Context
**Frequency**: 1+ tests
**Use case**: Parallel execution of blocking operations

```python
# From: tests/test_smartasync.py::test_bidirectional_scenario_a2
class Processor:
    @smartasync
    def process(self, data: str) -> str:
        time.sleep(0.01)  # Blocking work
        return data.upper()

# Concurrent execution
async def process_batch(items: list[str]):
    proc = Processor()
    results = await asyncio.gather(
        *[proc.process(item) for item in items]
    )
    return results

# All processed in parallel (different threads)
results = asyncio.run(process_batch(["a", "b", "c"]))
```

**Key points**:
- `asyncio.gather()` works with sync methods
- Each call runs in separate thread
- No event loop blocking
- True parallelism for CPU-bound work

## Pattern 4: __slots__ Classes
**Frequency**: 2+ tests
**Use case**: Memory-optimized classes

```python
# From: tests/test_smartasync.py::test_slots
class OptimizedManager:
    __slots__ = ('data',)

    def __init__(self):
        self.data = []

    @smartasync
    async def add_item(self, item: str) -> None:
        await asyncio.sleep(0.01)
        self.data.append(item)

# Works in both contexts
obj = OptimizedManager()
obj.add_item("item")  # Sync
await obj.add_item("item")  # Async
```

**Key points**:
- No special handling needed
- Works like regular methods
- Cache stored in decorator closure, not instance

## Pattern 5: Testing Without pytest-asyncio
**Frequency**: Multiple tests
**Use case**: Simple sync tests for async code

```python
# From: tests/test_smartasync.py::test_sync_context
@smartasync
async def fetch_user(user_id: int) -> dict:
    async with db.connect() as conn:
        return await conn.fetch_one(f"SELECT * FROM users WHERE id={user_id}")

# Sync test - no event loop setup!
def test_fetch_user():
    user = fetch_user(1)
    assert user['id'] == 1
    assert user['name'] == 'Alice'
```

**Key points**:
- No `@pytest.mark.asyncio` needed
- No `asyncio.run()` boilerplate
- Standard `def test_` functions
- Simpler test code

## Pattern 6: Cache Reset for Testing
**Frequency**: 3+ tests
**Use case**: Isolate test cases

```python
# From: tests/test_smartasync.py::test_cache_reset
class Service:
    @smartasync
    async def operation(self):
        await asyncio.sleep(0.01)

def test_something():
    svc = Service()
    # Reset cache for clean state
    svc.operation._smartasync_reset_cache()

    result = svc.operation()
    assert result is not None
```

**Key points**:
- `_smartasync_reset_cache()` resets context cache
- Use between tests for isolation
- Not needed in normal usage
- Only for testing edge cases

## Pattern 7: Error Propagation
**Frequency**: 2+ tests
**Use case**: Exception handling

```python
# From: tests/test_smartasync.py::test_error_propagation
@smartasync
async def failing_operation():
    await asyncio.sleep(0.01)
    raise ValueError("Something went wrong")

# Sync context
try:
    result = failing_operation()
except ValueError as e:
    print(f"Caught: {e}")

# Async context
try:
    result = await failing_operation()
except ValueError as e:
    print(f"Caught: {e}")
```

**Key points**:
- Exceptions propagate normally
- No special handling needed
- Works in both contexts
- Stack traces preserved

## Pattern 8: Mixed Sync/Async Methods in Same Class
**Frequency**: Multiple tests
**Use case**: Gradual migration, hybrid APIs

```python
# From: tests/test_smartasync.py::test_sync_context
class HybridService:
    @smartasync
    async def async_fetch(self) -> dict:
        async with httpx.AsyncClient() as client:
            return await client.get("...").json()

    @smartasync
    def sync_process(self, data: dict) -> dict:
        # Legacy sync processing
        return process_legacy(data)

# Both work in both contexts
async def main():
    svc = HybridService()
    data = await svc.async_fetch()  # Async method
    result = await svc.sync_process(data)  # Sync method (threaded)
```

**Key points**:
- Can mix async and sync methods
- All work in both contexts
- Async methods stay async internally
- Sync methods offloaded when in async context

## Anti-Pattern: Shared Instance Across Threads
**DON'T DO THIS**:

```python
# BAD: Shared instance in thread pool
from concurrent.futures import ThreadPoolExecutor

manager = Manager()  # Shared!

def worker(data):
    return manager.process(data)  # Race condition!

with ThreadPoolExecutor() as executor:
    results = executor.map(worker, items)
```

**Solution**: Instance per thread

```python
# GOOD: Instance per thread
def worker(data):
    manager = Manager()  # New instance
    return manager.process(data)

with ThreadPoolExecutor() as executor:
    results = executor.map(worker, items)
```

## Pattern Selection Guide

| Scenario | Pattern | Test Reference |
|----------|---------|----------------|
| CLI + async libs | Pattern 1 | test_sync_context |
| FastAPI + sync DB | Pattern 2 | test_bidirectional_scenario_a2 |
| Parallel blocking ops | Pattern 3 | test_bidirectional_scenario_a2 |
| Memory optimization | Pattern 4 | test_slots |
| Simple testing | Pattern 5 | test_sync_context |
| Test isolation | Pattern 6 | test_cache_reset |
| Error handling | Pattern 7 | test_error_propagation |
| Hybrid APIs | Pattern 8 | test_sync_context |

**See also**: EXAMPLES.md for complete working examples
