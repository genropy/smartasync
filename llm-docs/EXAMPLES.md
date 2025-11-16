# SmartAsync - Complete Examples

All snippets are copied from `tests/test_smartasync.py` and guaranteed to work.

---

## Example 1: Async Method Usable in Both Contexts
**From**: `tests/test_smartasync.py::test_sync_context`, `test_async_context`

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

# Sync context
obj = SimpleManager()
assert obj.async_method("one") == "Result: one"

# Async context
async def main():
    obj = SimpleManager()
    assert await obj.async_method("two") == "Result: two"

asyncio.run(main())
```

---

## Example 2: Sync Method Awaited Inside Async Code
**From**: `tests/test_smartasync.py::test_async_context`

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
    result = await obj.sync_method("legacy")
    assert result == "Sync: legacy"

asyncio.run(main())
```

**Key behavior**: Sync methods automatically run in a worker thread when awaited.

---

## Example 3: Async App Calling Legacy Sync Library
**From**: `tests/test_smartasync.py::test_bidirectional_scenario_a2`

```python
import asyncio, time
from smartasync import smartasync

class LegacyLibrary:
    def __init__(self):
        self.processed = []

    @smartasync
    def blocking_operation(self, data: str) -> str:
        time.sleep(0.01)  # Simulate blocking work
        result = data.upper()
        self.processed.append(result)
        return result

async def main():
    lib = LegacyLibrary()
    assert await lib.blocking_operation("legacy") == "LEGACY"

    results = await asyncio.gather(
        lib.blocking_operation("item1"),
        lib.blocking_operation("item2"),
        lib.blocking_operation("item3"),
    )
    assert results == ["ITEM1", "ITEM2", "ITEM3"]

asyncio.run(main())
```

---

## Example 4: Classes with `__slots__`
**From**: `tests/test_smartasync.py::test_slots`, `test_slots_async`

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

obj = ManagerWithSlots()
obj.add_item("a")
obj.add_item("b")
assert obj.get_count() == 2

async def main():
    obj = ManagerWithSlots()
    await obj.add_item("async1")
    await obj.add_item("async2")
    assert await obj.get_count() == 2

asyncio.run(main())
```

---

## Example 5: Cache Reset & Shared State
**From**: `tests/test_smartasync.py::test_cache_reset`, `test_cache_shared_between_instances`

```python
import asyncio
from smartasync import smartasync

class Service:
    @smartasync
    async def async_method(self, value: str) -> str:
        return value

# Shared cache between instances
svc1 = Service()
svc2 = Service()
assert svc1.async_method("one") == "one"
assert svc2.async_method("two") == "two"

# Reset cache for deterministic tests
svc1.async_method._smartasync_reset_cache()
svc2.async_method._smartasync_reset_cache()
```

---

## Example 6: Error Propagation in Both Contexts
**From**: `tests/test_smartasync.py::test_error_propagation`, `test_error_propagation_async`

```python
import asyncio
from smartasync import smartasync

@smartasync
async def buggy():
    await asyncio.sleep(0.01)
    raise RuntimeError("User error")

# Sync context
try:
    buggy()
except RuntimeError as e:
    assert "User error" in str(e)

# Async context
async def main():
    try:
        await buggy()
    except RuntimeError as e:
        assert "User error" in str(e)

asyncio.run(main())
```

---

## Example 7: Helpful Error When Loop Already Running
**From**: `tests/test_smartasync.py::test_sync_async_method_when_loop_running`

```python
import asyncio
from smartasync import smartasync

class SimpleManager:
    @smartasync
    async def async_method(self, value: str) -> str:
        await asyncio.sleep(0.01)
        return value

obj = SimpleManager()

def fake_asyncio_run(coro):
    coro.close()
    raise RuntimeError("asyncio.run() cannot be called from a running event loop")

asyncio_run_backup = asyncio.run
asyncio.run = fake_asyncio_run

try:
    obj.async_method("boom")
except RuntimeError as e:
    assert "Cannot call async_method() synchronously" in str(e)
finally:
    asyncio.run = asyncio_run_backup
```

---

## Example 8: Sync→Async Transition (Asymmetric Cache)
**From**: `tests/test_smartasync.py::test_sync_to_async_transition`

```python
import asyncio
from smartasync import smartasync

class TransitionService:
    def __init__(self):
        self.call_count = 0

    @smartasync
    async def async_method(self, value: str) -> str:
        self.call_count += 1
        await asyncio.sleep(0.01)
        return value

async def main():
    svc = TransitionService()
    assert await svc.async_method("first") == "first"
    assert await svc.async_method("second") == "second"
    assert svc.call_count == 2

asyncio.run(main())
```

---

## Example 9: Standalone Async Function
**From**: `tests/test_smartasync.py::test_standalone_function_sync`, `test_standalone_function_async`

```python
import asyncio
from smartasync import smartasync

@smartasync
async def add(x: int, y: int) -> int:
    await asyncio.sleep(0.01)
    return x + y

assert add(5, 3) == 8  # Sync caller

asyncio.run(add(1, 2))  # Async caller
```

---

## Example 10: Standalone Sync Function Awaited in Async Context
**From**: `tests/test_smartasync.py::test_standalone_sync_function_in_async`

```python
import asyncio, time
from smartasync import smartasync

@smartasync
def square(n: int) -> int:
    time.sleep(0.01)
    return n * n

async def main():
    assert await square(7) == 49
    assert await asyncio.gather(square(2), square(3)) == [4, 9]

asyncio.run(main())
```

---

**Need more context?** See `PATTERNS.md` for scenario summaries or `API.yaml` for signature details.
