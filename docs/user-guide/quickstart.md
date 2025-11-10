# Quick Start

This guide will get you up and running with SmartAsync in 5 minutes.

## Installation

```bash
pip install smartasync
```

## Your First SmartAsync Method

```python
from smartasync import smartasync
import httpx

class APIClient:
    @smartasync
    async def fetch_data(self, url: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
```

## Using in Sync Context

```python
# CLI tool or script
client = APIClient()
data = client.fetch_data("https://api.example.com/data")
print(data)
```

No `await` needed! SmartAsync automatically runs it with `asyncio.run()`.

## Using in Async Context

```python
# FastAPI or async application
async def handler():
    client = APIClient()
    data = await client.fetch_data("https://api.example.com/data")
    return data
```

Use `await` normally - SmartAsync returns a coroutine.

## Key Points

1. **Write async methods** using `async def` and `await`
2. **Add `@smartasync` decorator** to make them work everywhere
3. **Call without await** in sync contexts (CLI, scripts)
4. **Call with await** in async contexts (FastAPI, aiohttp)

## Next Steps

- [Basic Usage →](basic.md)
- [Usage Scenarios →](../scenarios/index.md)
- [How It Works →](../how-it-works/index.md)
