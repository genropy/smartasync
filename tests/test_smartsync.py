"""Test @smartsync decorator in standalone context."""

import asyncio
from smartsync import SmartSync, smartsync


class SimpleManager(SmartSync):
    """Simple test class with smartsync methods."""

    def __init__(self, _sync: bool = False):
        SmartSync.__init__(self, _sync)
        self.call_count = 0

    @smartsync
    async def async_method(self, value: str) -> str:
        """Async method decorated with @smartsync."""
        await asyncio.sleep(0.01)
        self.call_count += 1
        return f"Result: {value}"

    @smartsync
    def sync_method(self, value: str) -> str:
        """Sync method decorated with @smartsync (pass-through)."""
        self.call_count += 1
        return f"Sync: {value}"


class ManagerWithSlots(SmartSync):
    """Test class with __slots__."""

    __slots__ = ('data',)

    def __init__(self, _sync: bool = False):
        SmartSync.__init__(self, _sync)
        self.data = []

    @smartsync
    async def add_item(self, item: str) -> None:
        """Add item to data."""
        await asyncio.sleep(0.01)
        self.data.append(item)

    @smartsync
    async def get_count(self) -> int:
        """Get data count."""
        await asyncio.sleep(0.01)
        return len(self.data)


def test_sync_context():
    """Test sync context (no event loop)."""
    print("\n" + "="*60)
    print("TEST 1: Sync context (no event loop)")
    print("="*60)

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
    print("\n" + "="*60)
    print("TEST 2: Async context (with event loop)")
    print("="*60)

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

    # Call sync method
    print("\n3. Calling sync_method()...")
    result = obj.sync_method("sync")
    print(f"   Result: {result}")
    assert result == "Sync: sync"
    assert obj.call_count == 3
    print("   ✓ Sync method works!")

    print("\n✅ ASYNC CONTEXT TEST PASSED!")


def test_slots():
    """Test with __slots__."""
    print("\n" + "="*60)
    print("TEST 3: Class with __slots__")
    print("="*60)

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
    print("\n" + "="*60)
    print("TEST 4: Class with __slots__ (async)")
    print("="*60)

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
    print("\n" + "="*60)
    print("TEST 5: Cache reset")
    print("="*60)

    # Create fresh object and reset cache to ensure clean state
    obj = SimpleManager()
    obj.async_method._smartsync_reset_cache()

    print("\n1. First call...")
    result = obj.async_method("test1")
    assert result == "Result: test1"
    print("   ✓ Works!")

    print("\n2. Reset cache...")
    obj.async_method._smartsync_reset_cache()
    print("   ✓ Cache reset!")

    print("\n3. Call again after reset...")
    result = obj.async_method("test2")
    assert result == "Result: test2"
    print("   ✓ Works after reset!")

    print("\n✅ CACHE RESET TEST PASSED!")


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

    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)
    print("\nConclusion:")
    print("✅ Auto-detects sync context (no event loop)")
    print("✅ Auto-detects async context (with event loop)")
    print("✅ Works with __slots__")
    print("✅ Asymmetric caching works correctly")
    print("✅ Cache reset available")
    print("✅ Sync methods pass through")
    print("\n🚀 READY FOR USE!")
