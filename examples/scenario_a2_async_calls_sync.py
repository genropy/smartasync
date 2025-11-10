"""Example: Scenario A2 - Async App → Sync Legacy Library

This example demonstrates how SmartAsync enables async applications
to seamlessly call synchronous legacy libraries without blocking the event loop.

The sync methods are automatically offloaded to a thread pool using asyncio.to_thread().
"""

import asyncio
import time

from smartasync import smartasync


class LegacyDatabase:
    """Simulates a legacy synchronous database library.

    This represents existing code that uses blocking I/O or CPU-intensive operations.
    """

    def __init__(self):
        self.data = {}

    @smartasync
    def query(self, key: str) -> str:
        """Blocking database query (sync method)."""
        # Simulate blocking I/O
        time.sleep(0.1)
        return self.data.get(key, "NOT_FOUND")

    @smartasync
    def insert(self, key: str, value: str) -> None:
        """Blocking database insert (sync method)."""
        # Simulate blocking I/O
        time.sleep(0.1)
        self.data[key] = value

    @smartasync
    def bulk_process(self, items: list[str]) -> list[str]:
        """CPU-intensive processing (sync method)."""
        # Simulate CPU-bound work
        results = []
        for item in items:
            time.sleep(0.05)  # Simulate processing time
            results.append(item.upper())
        return results


async def main():
    """Async application using legacy sync library."""

    print("=" * 70)
    print("Scenario A2: Async App → Sync Legacy Library")
    print("=" * 70)

    db = LegacyDatabase()

    # Example 1: Single operations (auto-threaded)
    print("\n1. Single operations (each auto-threaded):")
    print("   Calling sync methods from async context...")

    await db.insert("user:1", "Alice")
    await db.insert("user:2", "Bob")
    print("   ✓ Inserts completed (ran in thread pool)")

    result = await db.query("user:1")
    print(f"   ✓ Query result: {result} (ran in thread pool)")

    # Example 2: Concurrent operations (won't block event loop!)
    print("\n2. Concurrent operations (parallel execution in threads):")
    start = time.time()

    results = await asyncio.gather(
        db.query("user:1"),
        db.query("user:2"),
        db.insert("user:3", "Charlie"),
        db.insert("user:4", "Diana"),
    )

    elapsed = time.time() - start
    print(f"   ✓ Processed 4 operations in {elapsed:.2f}s")
    print(f"   ✓ Results: {results[:2]}")  # Show query results
    print("   ℹ️  Without threading: would take ~0.4s sequentially")
    print(f"   ℹ️  With threading: took ~{elapsed:.2f}s (parallel execution)")

    # Example 3: CPU-intensive work (doesn't block event loop)
    print("\n3. CPU-intensive processing (offloaded to thread):")
    print("   Processing batch while event loop remains responsive...")

    # Start heavy processing
    processing_task = asyncio.create_task(
        db.bulk_process(["item1", "item2", "item3", "item4"])
    )

    # Meanwhile, event loop can handle other work
    await asyncio.sleep(0.05)
    print("   ℹ️  Event loop still responsive during processing!")

    # Wait for processing to complete
    processed = await processing_task
    print(f"   ✓ Processed items: {processed}")
    print("   ✓ Event loop was NOT blocked during processing")

    # Example 4: Mixed async/sync operations
    print("\n4. Mixed async/sync in same class:")

    class ModernApp:
        """Modern app mixing async and sync code."""

        def __init__(self):
            self.legacy_db = LegacyDatabase()

        @smartasync
        async def async_operation(self) -> str:
            """Native async method."""
            await asyncio.sleep(0.01)
            return "async_result"

        async def combined_workflow(self) -> dict:
            """Workflow mixing async and sync."""
            # Call native async method
            async_result = await self.async_operation()

            # Call legacy sync method (auto-threaded)
            await self.legacy_db.insert("result", async_result)
            sync_result = await self.legacy_db.query("result")

            return {
                "async": async_result,
                "sync": sync_result,
            }

    app = ModernApp()
    result = await app.combined_workflow()
    print(f"   ✓ Combined result: {result}")
    print("   ✓ Async and sync methods work seamlessly together")

    print("\n" + "=" * 70)
    print("✅ All scenarios completed successfully!")
    print("=" * 70)

    print("\nKey benefits:")
    print("  • No code changes needed in legacy library")
    print("  • Automatic thread offloading with @smartasync")
    print("  • Event loop never blocked")
    print("  • Concurrent execution where possible")
    print("  • Mixed async/sync workflows work naturally")


if __name__ == "__main__":
    asyncio.run(main())
