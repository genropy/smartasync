# Scenario A1: Sync Application Calling Async Libraries

**Role**: Application Developer
**Current State**: Writing sync application (CLI, script, multiprocess/multithread)
**Goal**: Use modern async libraries (httpx, aiofiles, async DB drivers)
**Challenge**: Don't want to deal with `asyncio.run()` everywhere

---

## Overview

You have a **synchronous application** (CLI tool, automation script, data processing pipeline) but want to use **modern async libraries** that offer better performance and features than their sync counterparts.

**Examples of async libraries you want to use**:
- `httpx.AsyncClient` (vs `requests`)
- `aiofiles` (vs built-in `open()`)
- `asyncpg` (vs `psycopg2`)
- `aiohttp` (vs `urllib`)

**Problem**: These libraries require async context, but your app is sync.

---

## Without SmartAsync

### Traditional Approach 1: Manual `asyncio.run()` Everywhere

```python
import asyncio
import httpx

class DataFetcher:
    async def _fetch_async(self, url: str):
        """Internal async implementation."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()

    def fetch(self, url: str):
        """Public sync wrapper."""
        return asyncio.run(self._fetch_async(url))

# Usage in sync code
fetcher = DataFetcher()
data = fetcher.fetch("https://api.example.com/users")
print(data)
```

**Pain Points**:
- ❌ Every method needs sync wrapper
- ❌ Code duplication
- ❌ Boilerplate: private async + public sync
- ❌ Easy to forget wrapper somewhere
- ❌ Verbose and repetitive

---

### Traditional Approach 2: Stay Sync with Sync Libraries

```python
import requests

class DataFetcher:
    def fetch(self, url: str):
        """Use sync library instead."""
        response = requests.get(url)
        return response.json()

# Usage
fetcher = DataFetcher()
data = fetcher.fetch("https://api.example.com/users")
```

**Pain Points**:
- ❌ Can't use modern async libraries
- ❌ Missing features (connection pooling, HTTP/2, etc.)
- ❌ Lower performance
- ❌ Code won't work if moved to async context later

---

### Traditional Approach 3: Make Everything Async

```python
import asyncio
import httpx

class DataFetcher:
    async def fetch(self, url: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()

# Usage - need to run event loop
async def main():
    fetcher = DataFetcher()
    data = await fetcher.fetch("https://api.example.com/users")
    print(data)

if __name__ == "__main__":
    asyncio.run(main())
```

**Pain Points**:
- ❌ Entire app becomes async
- ❌ All functions need `async def`
- ❌ All calls need `await`
- ❌ Complex for simple scripts
- ❌ Can't easily integrate with sync libraries

---

## With SmartAsync

### Solution

```python
import httpx
from smartasync import smartasync

class DataFetcher:
    @smartasync
    async def fetch(self, url: str):
        """Single implementation - works in both contexts!"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()

# Usage in sync code - NO await needed!
fetcher = DataFetcher()
data = fetcher.fetch("https://api.example.com/users")
print(data)

# Also works in async context (if you migrate later)
async def process():
    fetcher = DataFetcher()
    data = await fetcher.fetch("https://api.example.com/users")
    return data
```

**Benefits**:
- ✅ Single implementation
- ✅ Use async libraries from sync code
- ✅ No boilerplate
- ✅ Future-proof (works if you go async later)
- ✅ Clean, readable code

---

## Issues Impact on This Scenario

Based on [SCENARIOS-IMPACT-MATRIX.md](../SCENARIOS-IMPACT-MATRIX.md), here are the issues affecting Scenario A1:

### Issue #1: `_sync_mode` Ignored

**Impact**: ⚪ **NO IMPACT**

**Why**: Sync context is auto-detected correctly without needing `_sync_mode`.

**Status**: No fix needed for this scenario.

---

### Issue #2: Not Thread-Safe

**Impact**: 🟡 **DEGRADED** (if multi-threaded)

**Severity**: MEDIUM

**Problem**: If your sync app uses **multiple threads**, the cache can have race conditions.

#### Single-Threaded (NO PROBLEM)

```python
# ✅ SAFE: Single-threaded CLI
fetcher = DataFetcher()

for url in urls:
    data = fetcher.fetch(url)
    process(data)
```

#### Multi-Threaded (PROBLEM!)

```python
# ❌ UNSAFE: Multiple threads sharing instance
import threading

fetcher = DataFetcher()  # Shared across threads

def worker(url):
    data = fetcher.fetch(url)  # Race condition!
    process(data)

threads = [threading.Thread(target=worker, args=(url,)) for url in urls]
for t in threads:
    t.start()
```

#### Solution 1: Per-Thread Instances (Recommended)

```python
# ✅ SAFE: Each thread has its own instance
import threading

def worker(url):
    fetcher = DataFetcher()  # New instance per thread
    data = fetcher.fetch(url)
    process(data)

threads = [threading.Thread(target=worker, args=(url,)) for url in urls]
```

#### Solution 2: Thread-Local Storage (Advanced)

```python
# ✅ SAFE: Thread-local storage
import threading

thread_local = threading.local()

def get_fetcher():
    """Get or create thread-local fetcher."""
    if not hasattr(thread_local, 'fetcher'):
        thread_local.fetcher = DataFetcher()
    return thread_local.fetcher

def worker(url):
    fetcher = get_fetcher()
    data = fetcher.fetch(url)
    process(data)
```

#### Solution 3: Multiprocessing (If Applicable)

```python
# ✅ SAFE: Separate processes (no shared cache)
import multiprocessing

def worker(url):
    fetcher = DataFetcher()
    data = fetcher.fetch(url)
    process(data)

if __name__ == "__main__":
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(worker, urls)
```

---

### Issue #3: Missing Edge Case Tests

**Impact**: 🟢 **MINOR**

**Why**: Missing tests in SmartAsync library don't affect your app's runtime behavior.

**Status**: No action needed for users.

---

### Issue #4: Missing "When to Use" Documentation

**Impact**: 🟡 **DEGRADED**

**Problem**: You might not discover SmartAsync as a solution!

**Status**: This document addresses that gap.

---

## Decision Matrix

| Factor | Approach 1<br>(Manual `asyncio.run()`) | Approach 2<br>(Stay Sync) | Approach 3<br>(All Async) | **SmartAsync** |
|--------|-------|-------|-------|-------|
| Code duplication | High | None | None | **None** ✅ |
| Modern libraries | ✅ Yes | ❌ No | ✅ Yes | **✅ Yes** |
| Boilerplate | High | None | Medium | **None** ✅ |
| Future-proof | Medium | Low | High | **High** ✅ |
| Learning curve | Low | Low | High | **Low** ✅ |
| Thread safety | Good | Good | Good | **Needs care** ⚠️ |
| Performance (sync) | Good | Good | Good | **Good** ✅ |
| Multiprocess | Good | Good | Good | **Good** ✅ |

---

## When to Use SmartAsync for This Scenario

### ✅ USE SmartAsync if:

1. **Single-threaded sync app**
   - CLI tools
   - Sequential scripts
   - Single-process workers

2. **Multi-threaded with per-thread instances**
   - Thread pools with instance per thread
   - Thread-local storage pattern

3. **Multiprocess application**
   - Each process has separate cache
   - No shared state

4. **Want to use modern async libraries**
   - httpx, aiofiles, asyncpg, etc.
   - Better performance and features

5. **Future-proofing for async migration**
   - May go async later
   - Want compatible API

### ❌ DON'T use SmartAsync if:

1. **Heavy multi-threading with shared instances**
   - Many threads accessing same instance
   - Can't use per-thread instances

2. **Need guaranteed thread safety**
   - Critical applications
   - Can't tolerate race conditions

3. **Performance-critical tight loops**
   - Calling method millions of times
   - 100μs overhead per call matters

### 🤔 Consider Alternatives if:

1. **Simple use case**: Stay with sync libraries (requests, etc.)
2. **Already thread-safe**: Stick with current approach
3. **High-frequency calls**: Use explicit sync/async separation

---

## Real-World Example: Data Processing Pipeline

### Scenario

You're building a **data processing pipeline** that:
- Fetches data from REST API
- Downloads files from S3
- Writes results to database
- Runs in CLI (single-threaded)

### Before SmartAsync

```python
# pipeline.py
import asyncio
import httpx
import aiofiles
import asyncpg

class DataPipeline:
    async def _fetch_data_async(self, api_url: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            return response.json()

    def fetch_data(self, api_url: str):
        return asyncio.run(self._fetch_data_async(api_url))

    async def _download_file_async(self, url: str, path: str):
        async with httpx.AsyncClient() as client:
            async with aiofiles.open(path, 'wb') as f:
                async for chunk in client.stream('GET', url):
                    await f.write(chunk)

    def download_file(self, url: str, path: str):
        return asyncio.run(self._download_file_async(url, path))

    async def _save_to_db_async(self, data: dict):
        conn = await asyncpg.connect('postgresql://...')
        await conn.execute('INSERT INTO results VALUES ($1)', data)
        await conn.close()

    def save_to_db(self, data: dict):
        return asyncio.run(self._save_to_db_async(data))

# Usage
pipeline = DataPipeline()
data = pipeline.fetch_data("https://api.example.com/data")
pipeline.download_file("https://cdn.example.com/file.zip", "file.zip")
pipeline.save_to_db(data)
```

**Problems**:
- 3 async methods → 3 sync wrappers
- 6 methods total (2x duplication)
- Repetitive `asyncio.run()` calls
- Easy to forget wrapper

### After SmartAsync

```python
# pipeline.py
import httpx
import aiofiles
import asyncpg
from smartasync import smartasync

class DataPipeline:
    @smartasync
    async def fetch_data(self, api_url: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            return response.json()

    @smartasync
    async def download_file(self, url: str, path: str):
        async with httpx.AsyncClient() as client:
            async with aiofiles.open(path, 'wb') as f:
                async for chunk in client.stream('GET', url):
                    await f.write(chunk)

    @smartasync
    async def save_to_db(self, data: dict):
        conn = await asyncpg.connect('postgresql://...')
        await conn.execute('INSERT INTO results VALUES ($1)', data)
        await conn.close()

# Usage - same as before!
pipeline = DataPipeline()
data = pipeline.fetch_data("https://api.example.com/data")
pipeline.download_file("https://cdn.example.com/file.zip", "file.zip")
pipeline.save_to_db(data)
```

**Improvements**:
- ✅ 3 methods total (no duplication)
- ✅ Clean implementation
- ✅ No boilerplate
- ✅ Modern async libraries
- ✅ Same usage as before

---

## Migration Path

### From Sync Libraries to Async Libraries

#### Before (sync libraries)

```python
import requests

class APIClient:
    def fetch_users(self):
        response = requests.get("https://api.example.com/users")
        return response.json()

# Usage
client = APIClient()
users = client.fetch_users()
```

#### After (async libraries + SmartAsync)

```python
import httpx
from smartasync import smartasync

class APIClient:
    @smartasync
    async def fetch_users(self):
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/users")
            return response.json()

# Usage - SAME!
client = APIClient()
users = client.fetch_users()  # No await needed!
```

**Migration steps**:
1. Install SmartAsync: `pip install smartasync`
2. Import decorator: `from smartasync import smartasync`
3. Add `@smartasync` to methods
4. Change method to `async def`
5. Use async library (httpx instead of requests)
6. Keep usage code unchanged!

---

## Anti-Patterns

### ❌ Anti-Pattern 1: Shared Instance in Multi-Threading

```python
# ❌ BAD: Shared instance across threads
fetcher = DataFetcher()

def worker(url):
    data = fetcher.fetch(url)  # Race condition!
    process(data)

threads = [threading.Thread(target=worker, args=(url,)) for url in urls]
```

**Fix**: Use per-thread instances (see Issue #2 solutions above)

---

### ❌ Anti-Pattern 2: Nested `asyncio.run()`

```python
# ❌ BAD: Calling SmartAsync method from another async method with await
class Pipeline:
    @smartasync
    async def fetch(self, url: str):
        ...

    async def process(self):
        # This works but is unnecessary
        data = await self.fetch(url)  # Auto-detects async context correctly
```

**Fix**: This actually works fine! SmartAsync detects async context. Not an anti-pattern after all.

---

### ❌ Anti-Pattern 3: Using in Tight Performance Loop

```python
# ❌ BAD: Calling in performance-critical loop
fetcher = DataFetcher()

for i in range(1_000_000):
    data = fetcher.fetch(f"https://api.example.com/item/{i}")
    # 100μs × 1M = 100 seconds overhead!
```

**Fix**: Batch operations or use explicit async context:

```python
# ✅ GOOD: Batch in async context
async def fetch_all(urls):
    fetcher = DataFetcher()
    tasks = [fetcher.fetch(url) for url in urls]
    return await asyncio.gather(*tasks)

# Run once
results = asyncio.run(fetch_all(urls))
```

---

## Testing Strategy

### Test Your Code Using SmartAsync

```python
# test_pipeline.py
import pytest
from pipeline import DataPipeline

def test_fetch_data_sync():
    """Test in sync context (fast)."""
    pipeline = DataPipeline()
    data = pipeline.fetch_data("https://api.example.com/test")
    assert data['status'] == 'ok'

@pytest.mark.asyncio
async def test_fetch_data_async():
    """Test in async context (integration)."""
    pipeline = DataPipeline()
    data = await pipeline.fetch_data("https://api.example.com/test")
    assert data['status'] == 'ok'
```

---

## Performance Characteristics

### Overhead Analysis

| Operation | Time | Impact |
|-----------|------|--------|
| Network request | 10-200ms | Baseline |
| SmartAsync overhead (sync) | ~0.1ms | **0.05-1%** |
| SmartAsync overhead (async) | ~0.002ms | **0.001%** |

**Conclusion**: Overhead is **negligible** for network I/O operations.

---

## Checklist for This Scenario

Before using SmartAsync in Scenario A1, verify:

- [ ] My app is **single-threaded** OR I can use **per-thread instances**
- [ ] I want to use **async libraries** (httpx, aiofiles, etc.)
- [ ] I'm okay with **~100μs overhead** per call in sync context
- [ ] I don't need **guaranteed thread safety** with shared instances
- [ ] I've read the **thread safety mitigations** (if multi-threaded)

---

## Summary

**Scenario A1** (Sync App → Async Libs) is **✅ SUITABLE** for SmartAsync with these conditions:

| Condition | Status | Notes |
|-----------|--------|-------|
| Single-threaded | ✅ PERFECT | Zero issues |
| Multi-threaded | ⚠️ CAUTION | Use per-thread instances |
| Multiprocess | ✅ PERFECT | Separate caches |
| Network I/O | ✅ PERFECT | Overhead negligible |
| Tight loops | ❌ AVOID | Use explicit async |

**Primary benefits**:
1. Use modern async libraries from sync code
2. No boilerplate or duplication
3. Future-proof for async migration
4. Clean, readable code

**Primary risks**:
1. Thread safety (mitigable)
2. Slight overhead (~100μs per sync call)

---

## Related Scenarios

- [A2: Async App → Sync Libs](A2-async-app-sync-libs.md) - Opposite direction
- [A3: Dual-Mode Framework](A3-dual-mode-framework.md) - CLI + API
- [B1: Async Lib → Universal](../libraries/B1-async-lib-universal.md) - Library author perspective

---

## Further Reading

- [SCENARIOS-IMPACT-MATRIX.md](../SCENARIOS-IMPACT-MATRIX.md) - Issues impact across all scenarios
- [TECH-REPORT.md](../../TECH-REPORT.md) - Technical deep dive
- [Issue #2: Thread Safety](https://github.com/genropy/smartasync/issues/2) - Thread safety discussion

---

**Date**: 2025-11-10
**Scenario**: A1 - Sync App → Async Libs
**Status**: ✅ Suitable with thread safety awareness
