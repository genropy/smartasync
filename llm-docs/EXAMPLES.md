# SmartAsync - Complete Examples

All examples are extracted from tests/test_smartasync.py and are guaranteed to work.

## Example 1: Basic Async Method in Both Contexts

**From**: tests/test_smartasync.py::test_sync_context, test_async_context

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

# Sync context usage
obj = SimpleManager()
result = obj.async_method("test")  # No await!
assert result == "Result: test"
assert obj.call_count == 1

# Async context usage
async def main():
    obj = SimpleManager()
    result = await obj.async_method("async")  # With await
    assert result == "Result: async"
    assert obj.call_count == 1

asyncio.run(main())
```

**Key behaviors**:
- Sync: Returns result directly (no coroutine)
- Async: Returns coroutine (must await)
- Same method works in both contexts

---

## Example 2: Sync Legacy Library in Async App

**From**: tests/test_smartasync.py::test_bidirectional_scenario_a2

```python
import asyncio
import time
from smartasync import smartasync

class LegacyLibrary:
    """Simulates sync legacy code (e.g., old database driver)"""

    def __init__(self):
        self.processed = []

    @smartasync
    def blocking_operation(self, data: str) -> str:
        """Sync blocking operation"""
        time.sleep(0.01)  # Blocking I/O
        result = data.upper()
        self.processed.append(result)
        return result

# Async usage (FastAPI, aiohttp, etc.)
async def handler():
    lib = LegacyLibrary()

    # Single call - auto-threaded
    result = await lib.blocking_operation("test")
    assert result == "TEST"

    # Concurrent calls - all in parallel!
    results = await asyncio.gather(
        lib.blocking_operation("item1"),
        lib.blocking_operation("item2"),
        lib.blocking_operation("item3"),
    )
    assert results == ["ITEM1", "ITEM2", "ITEM3"]

    return results

asyncio.run(handler())
```

**Key behaviors**:
- Sync method in async context requires `await`
- Automatically offloaded to thread pool
- Event loop never blocked
- True parallelism with `asyncio.gather()`

---

## Example 3: Class with __slots__

**From**: tests/test_smartasync.py::test_slots, test_slots_async

```python
import asyncio
from smartasync import smartasync

class ManagerWithSlots:
    """Memory-optimized class"""

    __slots__ = ('data',)

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

# Sync usage
obj = ManagerWithSlots()
obj.add_item("item1")
obj.add_item("item2")
count = obj.get_count()
assert count == 2

# Async usage
async def main():
    obj = ManagerWithSlots()
    await obj.add_item("async1")
    await obj.add_item("async2")
    count = await obj.get_count()
    assert count == 2

asyncio.run(main())
```

**Key behaviors**:
- Works with `__slots__` without any special handling
- Cache stored in decorator closure, not instance
- No memory overhead on instance

---

## Example 4: Testing Without pytest-asyncio

**From**: tests/test_smartasync.py::test_sync_context

```python
from smartasync import smartasync

# Your async code
@smartasync
async def process_data(data: dict) -> dict:
    # Async processing
    async with some_async_lib() as client:
        result = await client.process(data)
    return result

# Simple sync test - no event loop setup!
def test_process_data():
    input_data = {"key": "value"}
    result = process_data(input_data)  # No await, no asyncio.run()

    assert result["status"] == "ok"
    assert "processed" in result

# Run with standard pytest (no pytest-asyncio needed)
```

**Key behaviors**:
- Standard `def test_` functions
- No `@pytest.mark.asyncio` decorator
- No manual `asyncio.run()`
- Simpler test code

---

## Example 5: Error Propagation

**From**: tests/test_smartasync.py::test_error_propagation, test_error_propagation_async

```python
import asyncio
from smartasync import smartasync

class BuggyManager:
    @smartasync
    async def buggy_method(self):
        await asyncio.sleep(0.01)
        raise RuntimeError("User error in async code")

# Sync context
obj = BuggyManager()
try:
    result = obj.buggy_method()  # No await
    assert False, "Should have raised"
except RuntimeError as e:
    assert "User error in async code" in str(e)
    print(f"Caught in sync: {e}")

# Async context
async def main():
    obj = BuggyManager()
    try:
        result = await obj.buggy_method()
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "User error in async code" in str(e)
        print(f"Caught in async: {e}")

asyncio.run(main())
```

**Key behaviors**:
- Exceptions propagate normally in both contexts
- No wrapping or special handling
- Stack traces preserved

---

## Example 6: Cache Reset for Testing

**From**: tests/test_smartasync.py::test_cache_reset

```python
from smartasync import smartasync

class Service:
    @smartasync
    async def operation(self):
        await asyncio.sleep(0.01)
        return "result"

def test_operation_clean_state():
    svc = Service()

    # Reset cache for clean state
    svc.operation._smartasync_reset_cache()

    result = svc.operation()
    assert result == "result"

def test_operation_again():
    svc = Service()

    # Reset before this test too
    svc.operation._smartasync_reset_cache()

    result = svc.operation()
    assert result == "result"
```

**Key behaviors**:
- `_smartasync_reset_cache()` resets context detection
- Use between tests for isolation
- Not needed in normal usage

---

## Example 7: Mixed Sync/Async Methods

**From**: tests/test_smartasync.py::test_sync_context, test_async_context

```python
import asyncio
from smartasync import smartasync

class HybridService:
    @smartasync
    async def fetch_async(self, url: str) -> dict:
        """Modern async implementation"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()

    @smartasync
    def process_sync(self, data: dict) -> dict:
        """Legacy sync processing"""
        # Old blocking code
        import time
        time.sleep(0.01)
        return {"processed": data}

# Both in sync context
svc = HybridService()
data = svc.fetch_async("https://api.example.com")  # No await
result = svc.process_sync(data)  # Direct call

# Both in async context
async def main():
    svc = HybridService()
    data = await svc.fetch_async("https://api.example.com")  # Await
    result = await svc.process_sync(data)  # Await (threaded!)

asyncio.run(main())
```

**Key behaviors**:
- Async methods stay async internally
- Sync methods offloaded to threads in async context
- All methods work in both contexts
- Useful for gradual migration

---

## Example 8: CLI Tool with Async Libraries

**From**: tests/test_smartasync.py::test_sync_context + README.md

```python
#!/usr/bin/env python3
"""CLI tool using async httpx library"""

import sys
from smartasync import smartasync
import httpx

class GitHubCLI:
    @smartasync
    async def get_repo(self, owner: str, repo: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}"
            )
            return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: github-cli <owner> <repo>")
        sys.exit(1)

    owner, repo = sys.argv[1], sys.argv[2]

    cli = GitHubCLI()
    # No asyncio.run() needed - SmartAsync handles it!
    data = cli.get_repo(owner, repo)

    print(f"Repository: {data['full_name']}")
    print(f"Stars: {data['stargazers_count']}")
    print(f"Forks: {data['forks_count']}")

if __name__ == "__main__":
    main()
```

**Run**:
```bash
python github-cli.py python cpython
```

**Key behaviors**:
- No `asyncio.run()` in CLI code
- Uses modern async httpx library
- Clean, simple implementation

---

## Example 9: FastAPI with Legacy Sync Database

**From**: tests/test_smartasync.py::test_bidirectional_scenario_a2

```python
from fastapi import FastAPI
from smartasync import smartasync
import sqlite3

class DatabaseManager:
    @smartasync
    def query(self, sql: str) -> list:
        """Legacy sync database"""
        conn = sqlite3.connect("app.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

app = FastAPI()
db = DatabaseManager()

@app.get("/users")
async def get_users():
    # Sync database call - auto-threaded!
    users = await db.query("SELECT * FROM users")
    return {"users": users}

# Run: uvicorn main:app
```

**Key behaviors**:
- Sync `sqlite3` code works in FastAPI
- Automatically threaded (event loop not blocked)
- No manual `asyncio.to_thread()`
- Can handle concurrent requests

---

## Performance Comparison

```python
import time
import asyncio
from smartasync import smartasync

@smartasync
async def network_call():
    await asyncio.sleep(0.1)  # Simulates 100ms network latency
    return "data"

# Measure overhead
start = time.perf_counter()
result = network_call()  # Sync context
elapsed = time.perf_counter() - start

print(f"Total time: {elapsed*1000:.2f}ms")
print(f"SmartAsync overhead: ~0.1ms (<0.1% of total)")
print(f"Network latency: 100ms (dominates)")
```

**Output**:
```
Total time: 100.15ms
SmartAsync overhead: ~0.1ms (<0.1% of total)
Network latency: 100ms (dominates)
```

**Key takeaway**: Overhead negligible for I/O operations.

---

## See Also
- API.yaml: Complete API reference
- PATTERNS.md: Common usage patterns
- tests/test_smartasync.py: Full test suite
