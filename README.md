<div align="center">

<img src="docs/assets/logo.png" alt="SmartAsync Logo" width="200"/>

# SmartAsync

> **Sync or async: this WAS the question**

**Unified sync/async API decorator with automatic context detection**

</div>

[![PyPI version](https://img.shields.io/pypi/v/smartasync.svg)](https://pypi.org/project/smartasync/)
[![Tests](https://github.com/genropy/smartasync/actions/workflows/test.yml/badge.svg)](https://github.com/genropy/smartasync/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/genropy/smartasync/branch/main/graph/badge.svg)](https://codecov.io/gh/genropy/smartasync)
[![Documentation Status](https://readthedocs.org/projects/smartasync/badge/?version=latest)](https://smartasync.readthedocs.io/en/latest/?badge=latest)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Part of Genro-Libs](https://img.shields.io/badge/Part%20of-Genro--Libs-blue)](https://github.com/softwell/genro-libs)
[![LLM Docs](https://img.shields.io/badge/LLM-Docs-purple)](llm-docs/)

SmartAsync allows you to write async methods once and call them in both sync and async contexts without modification. It automatically detects the execution context and adapts accordingly.

## Features

- ✅ **Automatic context detection**: Detects sync vs async execution context at runtime
- ✅ **Zero configuration**: Just apply the `@smartasync` decorator
- ✅ **Asymmetric caching**: Smart caching strategy for optimal performance
- ✅ **Class methods & standalone functions**: Decorate any callable (`def` or `async def`)
- ✅ **Compatible with `__slots__`**: Works with memory-optimized classes
- ✅ **Pure Python**: No dependencies beyond standard library

## Installation

```bash
pip install smartasync
```

## Quick Start

```python
from smartasync import smartasync
import asyncio

class DataManager:
    @smartasync
    async def fetch_data(self, url: str):
        """Fetch data - works in both sync and async contexts!"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()

# Sync context - no await needed
manager = DataManager()
data = manager.fetch_data("https://api.example.com/data")

# Async context - use await
async def main():
    manager = DataManager()
    data = await manager.fetch_data("https://api.example.com/data")

asyncio.run(main())
```

### Standalone function example

You can also decorate free functions—no class required:

```python
@smartasync
async def fetch_json(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        return await client.get(url).json()

# Sync context
data = fetch_json("https://api.example.com")

# Async context
async def main():
    data = await fetch_json("https://api.example.com")
```

## How It Works

SmartAsync uses `asyncio.get_running_loop()` to detect the execution context:

- **Sync context** (no event loop): Executes with `asyncio.run()`
- **Async context** (event loop running): Returns coroutine to be awaited

### Asymmetric Caching

SmartAsync uses an intelligent caching strategy:
- ✅ **Async context detected**: Cached forever (can't transition from async to sync)
- ⚠️ **Sync context**: Always rechecked (can transition from sync to async)

This ensures correct behavior while optimizing for the most common case (async contexts in web frameworks).

## Use Cases

### 1. CLI + HTTP API

```python
from smartasync import smartasync
from smpub import PublishedClass, ApiSwitcher

class DataHandler(PublishedClass):
    api = ApiSwitcher()

    @api
    @smartasync
    async def process_data(self, input_file: str):
        """Process data file."""
        async with aiofiles.open(input_file) as f:
            data = await f.read()
        return process(data)

# CLI usage (sync)
handler = DataHandler()
result = handler.process_data("data.csv")

# HTTP usage (async via FastAPI)
# Automatically works without modification!
```

### 2. Testing

```python
@smartasync
async def database_query(query: str):
    async with database.connect() as conn:
        return await conn.execute(query)

# Sync tests
def test_query():
    result = database_query("SELECT * FROM users")
    assert len(result) > 0

# Async tests
async def test_query_async():
    result = await database_query("SELECT * FROM users")
    assert len(result) > 0
```

### 3. Mixed Codebases

Perfect for gradually migrating sync code to async without breaking existing callers.

## Performance

- **Decoration time**: ~3-4 microseconds (one-time cost)
- **Sync context**: ~102 microseconds (dominated by `asyncio.run()` overhead)
- **Async context (first call)**: ~2.3 microseconds
- **Async context (cached)**: ~1.3 microseconds

For typical CLI tools and web APIs, this overhead is negligible compared to network latency (10-200ms).

## Advanced Usage

### With `__slots__`

SmartAsync works seamlessly with `__slots__` classes:

```python
from smartasync import smartasync

class OptimizedManager:
    __slots__ = ('data',)

    def __init__(self):
        self.data = []

    @smartasync
    async def add_item(self, item):
        await asyncio.sleep(0.01)  # Simulate I/O
        self.data.append(item)
```

### Cache Reset for Testing

```python
@smartasync
async def my_method():
    pass

# Reset cache between tests
my_method._smartasync_reset_cache()
```

## Limitations

- ⚠️ **Cannot transition from async to sync**: Once in async context, cannot move back to sync (this is correct behavior)
- ⚠️ **Sync overhead**: Always rechecks context in sync mode (~2 microseconds per call)

## Thread Safety

SmartAsync is **safe for all common use cases**:

✅ **Safe scenarios** (covers 99% of real-world usage):
- Single-threaded applications (CLI tools, scripts)
- Async event loops (inherently single-threaded)
- Web servers with request isolation (new instance per request)
- Thread pools with instance-per-thread pattern

⚠️ **Theoretical concern** (anti-pattern, not recommended):
- Sharing a single instance across multiple threads in a thread pool

**Why this isn't a real issue:**
The anti-pattern scenario defeats SmartAsync's purpose. If you're using thread pools with shared instances, you should use async workers instead for better performance and natural concurrency.

**Recommendation:** Create instances per thread/request, or better yet, use async patterns natively.

## Related Projects

SmartAsync is part of the **Genro-Libs toolkit**:

- [smartswitch](https://github.com/genropy/smartswitch) - Rule-based function dispatch
- [smpub](https://github.com/genropy/smpub) - CLI/API framework (uses SmartAsync for async handlers)
- [gtext](https://github.com/genropy/gtext) - Text transformation and templates

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

**Author**: Giovanni Porcari (Genropy Team)
**Part of**: [Genro-Libs](https://github.com/softwell/genro-libs) developer toolkit
