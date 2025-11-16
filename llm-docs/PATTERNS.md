# SmartAsync - Common Patterns

Patterns below come directly from `tests/test_smartasync.py`. Each snippet is runnable and cites its source test.

## Pattern 1: Async Method from Sync Code
**Use case**: CLI scripts calling async libraries  
**Tests**: `test_sync_context`

```python
import asyncio
from smartasync import smartasync

class SimpleManager:
    def __init__(self):
        self.call_count = 0

    @smartasync
    async def async_method(self, value: str) -> str:
        await asyncio.sleep(0.01)
        self.call_count += 1
        return f"Result: {value}"

obj = SimpleManager()
result = obj.async_method("test")  # No await!
assert result == "Result: test"
```

**Highlights**
- No `await` or `asyncio.run()` needed in sync context.
- Real value returned (not coroutine).
- ~102 µs overhead dominated by `asyncio.run()`.

---

## Pattern 2: Sync Method inside Async App
**Use case**: Async frameworks calling legacy sync code  
**Tests**: `test_async_context`

```python
import asyncio
from smartasync import smartasync

class SimpleManager:
    def __init__(self):
        self.call_count = 0

    @smartasync
    def sync_method(self, value: str) -> str:
        self.call_count += 1
        return f"Sync: {value}"

async def main():
    obj = SimpleManager()
    result = await obj.sync_method("legacy")  # Auto-threaded
    assert result == "Sync: legacy"

asyncio.run(main())
```

**Highlights**
- Must `await` in async context even for sync defs.
- Work is automatically offloaded via `asyncio.to_thread()`.
- Event loop stays responsive.

---

## Pattern 3: Concurrent Blocking Operations
**Use case**: Parallelizing CPU/I/O heavy sync routines  
**Tests**: `test_bidirectional_scenario_a2`

```python
import asyncio, time
from smartasync import smartasync

class LegacyLibrary:
    def __init__(self):
        self.processed = []

    @smartasync
    def blocking_operation(self, data: str) -> str:
        time.sleep(0.01)
        result = data.upper()
        self.processed.append(result)
        return result

async def main():
    lib = LegacyLibrary()
    results = await asyncio.gather(
        lib.blocking_operation("item1"),
        lib.blocking_operation("item2"),
        lib.blocking_operation("item3"),
    )
    assert results == ["ITEM1", "ITEM2", "ITEM3"]

asyncio.run(main())
```

**Highlights**
- Each sync call runs in a worker thread.
- `asyncio.gather()` works naturally.
- Ideal for CPU-bound or blocking libraries.

---

## Pattern 4: `__slots__` Support
**Use case**: Memory-optimized classes with async methods  
**Tests**: `test_slots`, `test_slots_async`

```python
import asyncio
from smartasync import smartasync

class ManagerWithSlots:
    __slots__ = ("data",)

    def __init__(self):
        self.data = []

    @smartasync
    async def add_item(self, item: str) -> None:
        await asyncio.sleep(0.01)
        self.data.append(item)

    @smartasync
    async def get_count(self) -> int:
        await asyncio.sleep(0.01)
        return len(self.data)
```

**Highlights**
- No per-instance attributes added.
- Decorator cache stored in closure, so `__slots__` remain intact.

---

## Pattern 5: Standalone Async Functions
**Use case**: Decorate functions, not just methods  
**Tests**: `test_standalone_function_sync`, `test_standalone_function_async`

```python
import asyncio
from smartasync import smartasync

@smartasync
async def fetch_data(value: str) -> str:
    await asyncio.sleep(0.01)
    return f"fetched-{value}"

# Sync usage
assert fetch_data("cli") == "fetched-cli"

# Async usage
asyncio.run(fetch_data("web"))
```

**Highlights**
- Works for free functions; no `self` argument required.
- Same async detection logic applies.

---

## Pattern 6: Standalone Sync Functions in Async Context
**Use case**: Offload pure functions without classes  
**Tests**: `test_standalone_sync_function_in_async`

```python
import asyncio, time
from smartasync import smartasync

@smartasync
def cpu_intensive(n: int) -> int:
    time.sleep(0.01)
    return n * n

async def main():
    result = await cpu_intensive(7)
    assert result == 49

    batch = await asyncio.gather(
        cpu_intensive(2), cpu_intensive(3), cpu_intensive(4)
    )
    assert batch == [4, 9, 16]

asyncio.run(main())
```

**Highlights**
- Perfect for helper functions or utility modules.
- Same semantics as class methods.

---

## Pattern 7: Cache Control & Shared State
**Use case**: Resetting or sharing context detection cache  
**Tests**: `test_cache_reset`, `test_cache_shared_between_instances`

```python
import asyncio
from smartasync import smartasync

class Service:
    @smartasync
    async def operation(self, payload: str) -> str:
        await asyncio.sleep(0.01)
        return f"ok:{payload}"

svc1 = Service()
svc2 = Service()

# Shared cache across instances
svc1.operation("a")
svc2.operation("b")

# Reset for deterministic tests
svc1.operation._smartasync_reset_cache()
```

**Highlights**
- Cache is per decorated function, shared across instances.
- `_smartasync_reset_cache()` only needed in tests.

---

## Pattern 8: Error Propagation & Helpful Messaging
**Use case**: Preserve user exceptions and guard against nested event loops  
**Tests**: `test_error_propagation`, `test_error_propagation_async`, `test_sync_async_method_when_loop_running`

```python
import asyncio
from smartasync import smartasync

@smartasync
async def buggy():
    await asyncio.sleep(0.01)
    raise RuntimeError("boom")

try:
    buggy()
except RuntimeError as e:
    assert "boom" in str(e)

# Helpful message if asyncio.run() invoked inside a running loop
# (simulated in tests by monkeypatching asyncio.run)
```

**Highlights**
- Exceptions bubble up unchanged in both contexts.
- Sync calls inside a running loop raise descriptive errors.

---

## Pattern 9: Sync→Async Transition (Asymmetric Caching)
**Use case**: Detect first async call and stick to async fast-path  
**Tests**: `test_sync_to_async_transition`

```python
import asyncio
from smartasync import smartasync

class TransitionService:
    def __init__(self):
        self.call_count = 0

    @smartasync
    async def work(self, value: str) -> str:
        self.call_count += 1
        await asyncio.sleep(0.01)
        return value

async def main():
    svc = TransitionService()
    await svc.work("first")
    await svc.work("second")  # Uses cached async flag

asyncio.run(main())
```

**Highlights**
- Once an async loop is detected it stays cached.
- Sync contexts are always re-checked, enabling CLI → async transitions.

---

## Anti-Pattern: Sharing One Instance Across Threads
**Issue**: Per-method cache is not thread-safe for a single shared instance  
**Tests**: Covered implicitly by design notes

```python
# BAD
shared = TransitionService()
def worker(data):
    return shared.work(data)

# GOOD
def worker(data):
    service = TransitionService()
    return service.work(data)
```

**Recommendation**
- Create instances per thread/task (best practice anyway).

---

## Pattern Lookup

| Scenario | Pattern | Test Reference |
|----------|---------|----------------|
| CLI calling async code | Pattern 1 | `test_sync_context` |
| Async app calling sync code | Pattern 2 | `test_async_context` |
| Parallel blocking work | Pattern 3 | `test_bidirectional_scenario_a2` |
| Memory-optimized classes | Pattern 4 | `test_slots`, `test_slots_async` |
| Standalone async helpers | Pattern 5 | `test_standalone_function_sync`, `test_standalone_function_async` |
| Standalone sync helpers | Pattern 6 | `test_standalone_sync_function_in_async` |
| Deterministic caching | Pattern 7 | `test_cache_reset`, `test_cache_shared_between_instances` |
| Exception handling | Pattern 8 | `test_error_propagation`, `test_error_propagation_async`, `test_sync_async_method_when_loop_running` |
| Sync→Async transitions | Pattern 9 | `test_sync_to_async_transition` |
