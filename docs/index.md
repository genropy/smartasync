# SmartAsync

**Bidirectional sync/async bridge for Python**

SmartAsync provides automatic context detection to seamlessly bridge synchronous and asynchronous Python code. Write your code once, use it everywhere.

## Key Features

- ✅ **Automatic Context Detection** - Detects sync vs async execution context at runtime
- ✅ **Bidirectional** - Supports both sync→async and async→sync
- ✅ **Zero Configuration** - Just apply the `@smartasync` decorator
- ✅ **Thread-Safe Offloading** - Sync code in async context runs in thread pool
- ✅ **Pure Python** - No dependencies beyond standard library
- ✅ **Python 3.10+** - Uses modern pattern matching

## Quick Example

```python
from smartasync import smartasync
import httpx

@smartasync
async def fetch_data(url: str):
    async with httpx.AsyncClient() as client:
        return await client.get(url).json()

# Sync context - no await needed!
data = fetch_data("https://api.example.com")

# Async context - use await
data = await fetch_data("https://api.example.com")
```

## Installation

```bash
pip install smartasync
```

## Use Cases

### Sync App → Async Libraries
CLI tools using modern async libraries (httpx, aiohttp) without boilerplate.

[Learn more →](scenarios/01-sync-app-async-libs.md)

### Async App → Sync Libraries
FastAPI/Django apps using legacy sync libraries (sqlite3, psycopg2) without blocking.

[Learn more →](scenarios/02-async-app-sync-libs.md)

### Unified Library API
Library authors providing single implementation for both sync and async users.

[Learn more →](scenarios/04-unified-library-api.md)

## How It Works

SmartAsync uses **pattern matching** to handle four execution scenarios:

| Context | Method | Behavior |
|---------|--------|----------|
| Sync → Async | `async def` | Execute with `asyncio.run()` |
| Sync → Sync | `def` | Direct pass-through |
| Async → Async | `async def` | Return coroutine (awaitable) |
| Async → Sync | `def` | Offload to thread with `asyncio.to_thread()` |

[Technical Details →](how-it-works/index.md)

## Next Steps

- [Installation Guide](user-guide/installation.md)
- [Quick Start Tutorial](user-guide/quickstart.md)
- [Usage Scenarios](scenarios/index.md)
- [API Reference](api/decorator.md)

## Part of Genro-Libs

SmartAsync is part of the [Genro-Libs toolkit](https://github.com/softwell/genro-libs) - a collection of focused, well-tested Python developer tools.

## License

MIT License - see [LICENSE](https://github.com/genropy/smartasync/blob/main/LICENSE) for details.
