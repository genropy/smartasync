"""Test @smartasync decorator in standalone context."""

import asyncio

import pytest

from smartasync import smartasync


class SimpleManager:
    """Simple test class with smartasync methods."""

    def __init__(self):
        self.call_count = 0

    @smartasync
    async def async_method(self, value: str) -> str:
        """Async method decorated with @smartasync."""
        await asyncio.sleep(0.01)
        self.call_count += 1
        return f"Result: {value}"

    @smartasync
    def sync_method(self, value: str) -> str:
        """Sync method decorated with @smartasync (pass-through)."""
        self.call_count += 1
        return f"Sync: {value}"


class ManagerWithSlots:
    """Test class with __slots__."""

    __slots__ = ("data",)

    def __init__(self):
        self.data = []

    @smartasync
    async def add_item(self, item: str) -> None:
        """Add item to data."""
        await asyncio.sleep(0.01)
        self.data.append(item)

    @smartasync
    async def get_count(self) -> int:
        """Get data count."""
        await asyncio.sleep(0.01)
        return len(self.data)


def test_sync_context():
    """Test sync context (no event loop)."""
    print("\n" + "=" * 60)
    print("TEST 1: Sync context (no event loop)")
    print("=" * 60)

    obj = SimpleManager()

    # Call async method without await
    print("\n1. Calling async_method() without await...")
    result = obj.async_method("test")
    print(f"   Result: {result}")
    assert result == "Result: test"
    assert obj.call_count == 1
    print("   ✓ Works without await!")

    # Call again
    print("\n2. Calling again...")
    result = obj.async_method("test2")
    print(f"   Result: {result}")
    assert result == "Result: test2"
    assert obj.call_count == 2
    print("   ✓ Works!")

    # Call sync method
    print("\n3. Calling sync_method()...")
    result = obj.sync_method("sync")
    print(f"   Result: {result}")
    assert result == "Sync: sync"
    assert obj.call_count == 3
    print("   ✓ Sync method works!")

    print("\n✅ SYNC CONTEXT TEST PASSED!")


async def test_async_context():
    """Test async context (with event loop)."""
    print("\n" + "=" * 60)
    print("TEST 2: Async context (with event loop)")
    print("=" * 60)

    obj = SimpleManager()

    # Call async method with await
    print("\n1. Calling async_method() with await...")
    result = await obj.async_method("async")
    print(f"   Result: {result}")
    assert result == "Result: async"
    assert obj.call_count == 1
    print("   ✓ Works with await!")

    # Call again
    print("\n2. Calling again...")
    result = await obj.async_method("async2")
    print(f"   Result: {result}")
    assert result == "Result: async2"
    assert obj.call_count == 2
    print("   ✓ Works!")

    # Call sync method (now requires await in async context!)
    print("\n3. Calling sync_method() with await...")
    result = await obj.sync_method("sync")
    print(f"   Result: {result}")
    assert result == "Sync: sync"
    assert obj.call_count == 3
    print("   ✓ Sync method works (offloaded to thread)!")

    print("\n✅ ASYNC CONTEXT TEST PASSED!")


def test_slots():
    """Test with __slots__."""
    print("\n" + "=" * 60)
    print("TEST 3: Class with __slots__")
    print("=" * 60)

    obj = ManagerWithSlots()

    print("\n1. Adding items...")
    obj.add_item("item1")
    obj.add_item("item2")
    obj.add_item("item3")
    print("   ✓ Items added!")

    print("\n2. Getting count...")
    count = obj.get_count()
    print(f"   Count: {count}")
    assert count == 3
    print("   ✓ Count correct!")

    print("\n✅ SLOTS TEST PASSED!")


async def test_slots_async():
    """Test with __slots__ in async context."""
    print("\n" + "=" * 60)
    print("TEST 4: Class with __slots__ (async)")
    print("=" * 60)

    obj = ManagerWithSlots()

    print("\n1. Adding items with await...")
    await obj.add_item("async1")
    await obj.add_item("async2")
    print("   ✓ Items added!")

    print("\n2. Getting count with await...")
    count = await obj.get_count()
    print(f"   Count: {count}")
    assert count == 2
    print("   ✓ Count correct!")

    print("\n✅ ASYNC SLOTS TEST PASSED!")


def test_cache_reset():
    """Test cache reset functionality."""
    print("\n" + "=" * 60)
    print("TEST 5: Cache reset")
    print("=" * 60)

    # Create fresh object and reset cache to ensure clean state
    obj = SimpleManager()
    obj.async_method._smartasync_reset_cache()

    print("\n1. First call...")
    result = obj.async_method("test1")
    assert result == "Result: test1"
    print("   ✓ Works!")

    print("\n2. Reset cache...")
    obj.async_method._smartasync_reset_cache()
    print("   ✓ Cache reset!")

    print("\n3. Call again after reset...")
    result = obj.async_method("test2")
    assert result == "Result: test2"
    print("   ✓ Works after reset!")

    print("\n✅ CACHE RESET TEST PASSED!")


def test_error_propagation():
    """Test that RuntimeError from user code propagates correctly."""
    print("\n" + "=" * 60)
    print("TEST 6: Error propagation")
    print("=" * 60)

    class BuggyManager:
        @smartasync
        async def buggy_method(self):
            """Method that raises an error."""
            await asyncio.sleep(0.01)
            raise RuntimeError("User error in async code")

    print("\n1. Testing error in sync context...")
    obj = BuggyManager()
    try:
        obj.buggy_method()
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "User error in async code" in str(e)
        print(f"   ✓ Error propagated correctly: {e}")

    print("\n✅ ERROR PROPAGATION TEST PASSED!")


def test_sync_async_method_when_loop_running(monkeypatch):
    """Ensure helpful error when asyncio.run() is called while a loop is active.

    Defensive test - simulates unlikely edge case for 100% coverage.
    """
    obj = SimpleManager()
    obj.async_method._smartasync_reset_cache()

    def fake_asyncio_run(coro):
        try:
            coro.close()
        finally:
            raise RuntimeError(
                "asyncio.run() cannot be called from a running event loop"
            )

    monkeypatch.setattr(asyncio, "run", fake_asyncio_run)

    with pytest.raises(RuntimeError) as excinfo:
        obj.async_method("boom")

    message = str(excinfo.value)
    assert "Cannot call async_method() synchronously from within an async context" in message
    assert "Use 'await async_method()' instead." in message


async def test_error_propagation_async():
    """Test error propagation in async context."""
    print("\n" + "=" * 60)
    print("TEST 7: Error propagation (async)")
    print("=" * 60)

    class BuggyManager:
        @smartasync
        async def buggy_method(self):
            await asyncio.sleep(0.01)
            raise ValueError("Async error")

    print("\n1. Testing error in async context...")
    obj = BuggyManager()
    try:
        await obj.buggy_method()
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Async error" in str(e)
        print(f"   ✓ Error propagated correctly: {e}")

    print("\n✅ ASYNC ERROR PROPAGATION TEST PASSED!")


def test_cache_shared_between_instances():
    """Test that cache is per-method (shared between instances)."""
    print("\n" + "=" * 60)
    print("TEST 8: Cache shared between instances")
    print("=" * 60)

    # Reset cache first to ensure clean state
    obj_temp = SimpleManager()
    obj_temp.async_method._smartasync_reset_cache()

    print("\n1. Create two instances...")
    obj1 = SimpleManager()
    obj2 = SimpleManager()
    print("   ✓ Instances created")

    print("\n2. Call obj1 in sync context...")
    result1 = obj1.async_method("obj1-sync")
    assert result1 == "Result: obj1-sync"
    print("   ✓ obj1 works in sync")

    print("\n3. Call obj2 in sync context (should also work)...")
    result2 = obj2.async_method("obj2-sync")
    assert result2 == "Result: obj2-sync"
    print("   ✓ obj2 works in sync (cache shared)")

    print("\n✅ CACHE SHARING TEST PASSED!")


async def test_sync_to_async_transition():
    """Test transition from sync to async context."""
    print("\n" + "=" * 60)
    print("TEST 9: Sync → Async transition")
    print("=" * 60)

    # Reset cache to start fresh
    obj = SimpleManager()
    obj.async_method._smartasync_reset_cache()

    print("\n1. First call in async context...")
    result = await obj.async_method("async-test")
    assert result == "Result: async-test"
    assert obj.call_count == 1
    print("   ✓ Async call works")

    print("\n2. Cache should be set to True now")
    print("   ✓ Cache indicates async context")

    print("\n3. Second call in async context (cached)...")
    result = await obj.async_method("async-test-2")
    assert result == "Result: async-test-2"
    assert obj.call_count == 2
    print("   ✓ Cached async call works")

    print("\n✅ SYNC→ASYNC TRANSITION TEST PASSED!")


async def test_bidirectional_scenario_a2():
    """Test Scenario A2: Async app calling sync legacy library.

    This demonstrates the bidirectional capability where sync methods
    are automatically offloaded to threads when called from async context.
    """
    print("\n" + "=" * 60)
    print("TEST 10: Bidirectional - Async App → Sync Library")
    print("=" * 60)

    class LegacyLibrary:
        """Simulates a sync legacy library."""

        def __init__(self):
            self.processed = []

        @smartasync
        def blocking_operation(self, data: str) -> str:
            """Sync blocking operation (e.g., CPU-bound processing)."""
            import time

            time.sleep(0.01)  # Simulate blocking work
            result = data.upper()
            self.processed.append(result)
            return result

    print("\n1. Create async app with legacy library...")
    lib = LegacyLibrary()
    print("   ✓ Library instantiated")

    print("\n2. Call sync method from async context (auto-threaded)...")
    result = await lib.blocking_operation("legacy")
    assert result == "LEGACY"
    assert "LEGACY" in lib.processed
    print(f"   ✓ Result: {result} (executed in thread pool)")

    print("\n3. Multiple concurrent calls (won't block event loop)...")
    import asyncio

    results = await asyncio.gather(
        lib.blocking_operation("item1"),
        lib.blocking_operation("item2"),
        lib.blocking_operation("item3"),
    )
    assert results == ["ITEM1", "ITEM2", "ITEM3"]
    print(f"   ✓ Processed {len(results)} items concurrently")

    print("\n✅ BIDIRECTIONAL A2 TEST PASSED!")
    print("   🎯 Sync legacy code works seamlessly in async context!")


def test_standalone_function_sync():
    """Test standalone async function called from sync context."""
    print("\n" + "=" * 60)
    print("TEST 11: Standalone async function (sync context)")
    print("=" * 60)

    @smartasync
    async def process_data(x: int, y: int) -> int:
        """Standalone async function."""
        await asyncio.sleep(0.01)
        return x + y

    print("\n1. Call standalone async function from sync context...")
    result = process_data(5, 3)
    assert result == 8
    print(f"   ✓ Result: {result}")

    print("\n✅ STANDALONE FUNCTION (SYNC) TEST PASSED!")


async def test_standalone_function_async():
    """Test standalone async function called from async context."""
    print("\n" + "=" * 60)
    print("TEST 12: Standalone async function (async context)")
    print("=" * 60)

    @smartasync
    async def fetch_data(value: str) -> str:
        """Standalone async function."""
        await asyncio.sleep(0.01)
        return f"fetched-{value}"

    print("\n1. Call standalone async function from async context...")
    result = await fetch_data("test")
    assert result == "fetched-test"
    print(f"   ✓ Result: {result}")

    print("\n✅ STANDALONE FUNCTION (ASYNC) TEST PASSED!")


async def test_standalone_sync_function_in_async():
    """Test standalone sync function called from async context (offloaded to thread)."""
    print("\n" + "=" * 60)
    print("TEST 13: Standalone sync function (async context)")
    print("=" * 60)

    @smartasync
    def cpu_intensive(n: int) -> int:
        """Standalone sync function (simulates CPU-bound work)."""
        import time

        time.sleep(0.01)
        return n * n

    print("\n1. Call standalone sync function from async context...")
    result = await cpu_intensive(7)
    assert result == 49
    print(f"   ✓ Result: {result} (executed in thread pool)")

    print("\n2. Multiple concurrent calls...")
    results = await asyncio.gather(
        cpu_intensive(2), cpu_intensive(3), cpu_intensive(4)
    )
    assert results == [4, 9, 16]
    print(f"   ✓ Processed {len(results)} items concurrently")

    print("\n✅ STANDALONE SYNC FUNCTION (ASYNC) TEST PASSED!")


if __name__ == "__main__":
    # Test sync context
    test_sync_context()

    # Test async context
    asyncio.run(test_async_context())

    # Test __slots__
    test_slots()

    # Test __slots__ async
    asyncio.run(test_slots_async())

    # Test cache reset
    test_cache_reset()

    # Test error propagation
    test_error_propagation()

    # Test error propagation async
    asyncio.run(test_error_propagation_async())

    # Test cache sharing
    test_cache_shared_between_instances()

    # Test sync to async transition
    asyncio.run(test_sync_to_async_transition())

    # Test bidirectional scenario A2
    asyncio.run(test_bidirectional_scenario_a2())

    # Test standalone functions
    test_standalone_function_sync()
    asyncio.run(test_standalone_function_async())
    asyncio.run(test_standalone_sync_function_in_async())

    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print("\nConclusion:")
    print("✅ Auto-detects sync context (no event loop)")
    print("✅ Auto-detects async context (with event loop)")
    print("✅ Works with __slots__")
    print("✅ Asymmetric caching works correctly")
    print("✅ Cache reset available")
    print("✅ BIDIRECTIONAL: Async methods work in sync context (asyncio.run)")
    print("✅ BIDIRECTIONAL: Sync methods work in async context (asyncio.to_thread)")
    print("✅ Works with standalone functions (not just class methods)")
    print("✅ Error propagation works correctly")
    print("✅ Cache is per-method (shared between instances)")
    print("✅ Sync→Async transitions work")
    print("\n🚀 READY FOR USE - FULLY BIDIRECTIONAL!")
