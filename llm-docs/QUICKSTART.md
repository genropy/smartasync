# SmartAsync - 30 Second Guide

## Install
```bash
pip install smartasync
```

## Core Concept
Bidirectional decorator: write async code once, call from sync OR async contexts automatically.

## Basic Usage
```python
import asyncio
from smartasync import smartasync

class Manager:
    @smartasync
    async def fetch(self, value: str) -> str:
        await asyncio.sleep(0.01)
        return f"Result: {value}"

# Sync context - NO await needed
obj = Manager()
result = obj.fetch("test")  # Returns "Result: test"

# Async context - WITH await
async def main():
    obj = Manager()
    result = await obj.fetch("test")  # Returns "Result: test"
```
*From: tests/test_smartasync.py::test_sync_context, test_async_context*

### Standalone Functions
```python
import asyncio
from smartasync import smartasync

@smartasync
async def fetch(value: str) -> str:
    await asyncio.sleep(0.01)
    return f"Result: {value}"

result = fetch("sync-call")      # Sync context
result_async = await fetch("async-call")  # Async context
```
*From: tests/test_smartasync.py::test_standalone_function_sync, test_standalone_function_async*

## Key Features
- **Bidirectional**: Async callables work in sync context (uses `asyncio.run()`), sync callables work in async context (uses `asyncio.to_thread()`)
- **Zero config**: Just add `@smartasync` decorator
- **Auto-detection**: Runtime context detection via `asyncio.get_running_loop()`
- **Performance**: ~1-2μs overhead in async context (cached), ~100μs in sync context
- **Standalone friendly**: Works for free functions and class methods alike
- **__slots__ compatible**: Works with memory-optimized classes

## Critical Behaviors
- **Async → Sync**: Async methods in sync context execute with `asyncio.run()`
- **Sync → Async**: Sync methods in async context offload to thread pool (prevents blocking)
- **Caching**: Asymmetric - caches async context forever, always rechecks sync context
- **Thread offloading**: Sync code in async context runs in `asyncio.to_thread()` automatically

## Next
- API.yaml: Complete reference
- PATTERNS.md: Usage patterns
- EXAMPLES.md: Full working examples
