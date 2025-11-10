# SmartAsync - Scenarios vs Issues Impact Matrix

**Purpose**: Understand how each open issue affects different usage scenarios and identify mitigations.

**Date**: 2025-11-10
**Status**: Analysis for v0.1.0

---

## Open Issues Summary

| Issue | Title | Severity | Type |
|-------|-------|----------|------|
| [#1](https://github.com/genropy/smartasync/issues/1) | `_sync_mode` parameter ignored | 🔴 HIGH | Bug |
| [#2](https://github.com/genropy/smartasync/issues/2) | Not thread-safe | 🟡 MEDIUM | Limitation |
| [#3](https://github.com/genropy/smartasync/issues/3) | Missing edge case tests | 🟡 MEDIUM | Enhancement |
| [#4](https://github.com/genropy/smartasync/issues/4) | Missing "When to Use" docs | 🔴 HIGH | Documentation |

---

## Scenarios Overview

### Application Scenarios (Consumer Perspective)

| ID | Scenario | Description | Typical User |
|----|----------|-------------|--------------|
| **A1** | Sync App → Async Libs | Sync application calling async libraries | CLI tool, automation script |
| **A2** | Async App → Sync Libs | Async application calling sync libraries | FastAPI, web server |
| **A3** | Dual-Mode Framework | Same code for CLI and web API | smpub framework |
| **A4** | Testing | Mix of sync and async tests | Test suite |

### Library Scenarios (Provider Perspective)

| ID | Scenario | Description | Typical User |
|----|----------|-------------|--------------|
| **B1** | Async Lib → Universal | Async library for both sync/async users | SDK author |
| **B2** | Sync Lib → Future Async | Prepare sync lib for async migration | Legacy lib maintainer |

---

## Impact Matrix

### Legend

- 🔴 **BLOCKING**: Issue prevents scenario from working
- 🟡 **DEGRADED**: Scenario works but with limitations
- 🟢 **MINOR**: Issue has minimal impact
- ⚪ **NO IMPACT**: Issue doesn't affect scenario
- 💡 **MITIGATION**: Workaround available

---

## Scenario A1: Sync App → Async Libs

**Example**: CLI tool using httpx, aiofiles

```python
# CLI tool (sync context)
from mylib import DataFetcher

fetcher = DataFetcher()
data = fetcher.fetch("https://api.example.com")  # No await!
print(data)
```

### Impact Analysis

| Issue | Impact | Severity | Details |
|-------|--------|----------|---------|
| **#1** (_sync_mode) | ⚪ NO IMPACT | - | Sync context auto-detected correctly without `_sync_mode` |
| **#2** (Thread safety) | 🟡 DEGRADED | MEDIUM | **Problem**: Multi-threaded CLI with concurrent calls<br>**Mitigation**: Per-thread instances or sequential execution |
| **#3** (Tests) | 🟢 MINOR | LOW | Missing tests don't affect runtime behavior |
| **#4** (Docs) | 🟡 DEGRADED | MEDIUM | **Problem**: Users don't know this is a good use case<br>**Mitigation**: Read TECH-REPORT.md |

### Recommendations

✅ **SUITABLE** for this scenario with caveats:

1. **Single-threaded CLI**: ✅ Perfect, zero issues
2. **Multi-threaded CLI**: ⚠️ Use per-thread instances or locks
3. **Multiprocess**: ✅ Each process has separate cache

### Example: Multi-threading Mitigation

```python
import threading

# ❌ PROBLEMATIC: Shared instance
fetcher = DataFetcher()

def worker():
    fetcher.fetch("https://api.example.com")  # Race condition!

threads = [threading.Thread(target=worker) for _ in range(10)]

# ✅ SOLUTION 1: Per-thread instances
import threading

def worker():
    fetcher = DataFetcher()  # New instance per thread
    fetcher.fetch("https://api.example.com")

# ✅ SOLUTION 2: Thread-local storage
thread_local = threading.local()

def worker():
    if not hasattr(thread_local, 'fetcher'):
        thread_local.fetcher = DataFetcher()
    thread_local.fetcher.fetch("https://api.example.com")
```

---

## Scenario A2: Async App → Sync Libs

**Example**: FastAPI calling legacy sync library

```python
# FastAPI (async context)
from fastapi import FastAPI
from legacy_lib import DatabaseClient

app = FastAPI()
db = DatabaseClient()  # Legacy sync lib

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    # db.query() is sync, but decorated with @smartasync
    user = await db.query(f"SELECT * FROM users WHERE id={user_id}")
    return user
```

### Impact Analysis

| Issue | Impact | Severity | Details |
|-------|--------|----------|---------|
| **#1** (_sync_mode) | ⚪ NO IMPACT | - | Async context auto-detected correctly |
| **#2** (Thread safety) | 🟢 MINOR | LOW | FastAPI is single-threaded (async event loop), no race conditions |
| **#3** (Tests) | 🟢 MINOR | LOW | Missing tests don't affect runtime |
| **#4** (Docs) | 🟡 DEGRADED | MEDIUM | Users don't know this is a good use case |

### Recommendations

✅ **SUITABLE** - Minimal issues

**Why it works well**:
- Async frameworks are single-threaded (event loop)
- No thread safety concerns
- Cache is set once (async context) and never changes

---

## Scenario A3: Dual-Mode Framework (CLI + API)

**Example**: smpub - same code for CLI and web API

```python
from smartasync import smartasync
from smpub import PublishedClass, ApiSwitcher

class DataHandler(PublishedClass):
    api = ApiSwitcher()

    @api
    @smartasync
    async def process_file(self, path: str):
        async with aiofiles.open(path) as f:
            data = await f.read()
        return await self._process(data)

# CLI: python cli.py process data.csv
# API: POST /process {"file": "data.csv"}
```

### Impact Analysis

| Issue | Impact | Severity | Details |
|-------|--------|----------|---------|
| **#1** (_sync_mode) | 🟡 DEGRADED | MEDIUM | **Problem**: Can't force sync mode in async context or vice versa<br>**Use case**: Testing CLI behavior in async test suite<br>**Mitigation**: Separate test contexts or use `_smartasync_reset_cache()` |
| **#2** (Thread safety) | 🟢 MINOR | LOW | CLI is single-threaded, API is async event loop |
| **#3** (Tests) | 🟡 DEGRADED | MEDIUM | **Problem**: Can't test context transitions robustly<br>**Impact**: Uncertainty about edge cases |
| **#4** (Docs) | 🔴 BLOCKING | HIGH | **Problem**: This is THE primary use case but not documented!<br>**Impact**: Potential users don't discover SmartAsync |

### Recommendations

✅ **SUITABLE** - This is the **PRIMARY USE CASE**

**Critical**: Issue #4 must be fixed - this scenario should be prominently documented.

**Issue #1 Impact**: Would be nice to have for testing, but not critical for production use.

---

## Scenario A4: Testing (Sync + Async Tests)

**Example**: Test suite with both sync and async tests

```python
import pytest
from myapp import DataProcessor

# Sync tests (fast unit tests)
def test_process_data_sync():
    processor = DataProcessor()
    result = processor.process("test.csv")  # No await
    assert result.status == "ok"

# Async tests (integration tests)
@pytest.mark.asyncio
async def test_process_data_async():
    processor = DataProcessor()
    result = await processor.process("test.csv")  # Await
    assert result.status == "ok"
```

### Impact Analysis

| Issue | Impact | Severity | Details |
|-------|--------|----------|---------|
| **#1** (_sync_mode) | 🟡 DEGRADED | MEDIUM | **Problem**: Can't force sync execution in async test context<br>**Use case**: Test sync behavior from async test runner<br>**Mitigation**: Split test files or use `_smartasync_reset_cache()` |
| **#2** (Thread safety) | 🟡 DEGRADED | MEDIUM | **Problem**: Parallel test execution with pytest-xdist<br>**Mitigation**: Run tests sequentially or per-worker instances |
| **#3** (Tests) | 🔴 BLOCKING | HIGH | **Problem**: Can't verify SmartAsync behavior in tests without proper test suite!<br>**Impact**: Uncertainty about correctness |
| **#4** (Docs) | 🟡 DEGRADED | MEDIUM | Users don't know testing is a good use case |

### Recommendations

⚠️ **SUITABLE WITH CAUTION**

**Issue #3 is critical**: Without proper tests for SmartAsync itself, how can users trust it in their tests?

### Mitigations for Testing

```python
# ✅ Reset cache between tests
import pytest

@pytest.fixture(autouse=True)
def reset_smartasync_cache():
    """Reset cache before each test."""
    from myapp import DataProcessor
    if hasattr(DataProcessor.process, '_smartasync_reset_cache'):
        DataProcessor.process._smartasync_reset_cache()
    yield

# ✅ Separate test files
# tests/sync/test_processor_sync.py
def test_process_sync():
    ...

# tests/async/test_processor_async.py
@pytest.mark.asyncio
async def test_process_async():
    ...

# ✅ Run sequentially
# pytest -n 0  (disable parallel execution)
```

---

## Scenario B1: Async Lib → Universal Use

**Example**: SDK author writing async library for all users

```python
# Your library (mylib/client.py)
import httpx
from smartasync import smartasync

class APIClient:
    """SDK for external API - async internally."""

    @smartasync
    async def get_user(self, user_id: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.example.com/users/{user_id}")
            return response.json()

# User in sync script
from mylib import APIClient
client = APIClient()
user = client.get_user("123")  # ✅ Works without await

# User in async app
async def main():
    client = APIClient()
    user = await client.get_user("123")  # ✅ Works with await
```

### Impact Analysis

| Issue | Impact | Severity | Details |
|-------|--------|----------|---------|
| **#1** (_sync_mode) | 🟡 DEGRADED | MEDIUM | **Problem**: Library can't offer explicit sync/async modes<br>**Use case**: `APIClient(mode='sync')` for consistency<br>**Mitigation**: Document that auto-detection always used |
| **#2** (Thread safety) | 🔴 BLOCKING | HIGH | **Problem**: Users may use your library in multi-threaded apps!<br>**Impact**: Your library crashes in some user environments<br>**Mitigation**: Document thread-safety limitations prominently |
| **#3** (Tests) | 🟡 DEGRADED | MEDIUM | **Problem**: Library author can't fully test both usage modes<br>**Impact**: Bugs slip through |
| **#4** (Docs) | 🔴 BLOCKING | HIGH | **Problem**: Library users don't know they can use it both ways<br>**Impact**: Lost adoption |

### Recommendations

⚠️ **SUITABLE BUT RISKY** for library authors

**Critical concerns**:

1. **Issue #2 is BLOCKING**: If your users use threads, they'll file bugs against YOUR library
2. **Issue #4 is BLOCKING**: Users need to know this feature exists

### Library Author Checklist

When using SmartAsync in your public library:

```markdown
## In your library's README.md

### ⚠️ Thread Safety

This library uses SmartAsync for automatic sync/async detection.
**NOT thread-safe** - use one of these approaches:

1. **Per-thread instances** (recommended):
   ```python
   import threading
   thread_local = threading.local()

   def get_client():
       if not hasattr(thread_local, 'client'):
           thread_local.client = APIClient()
       return thread_local.client
   ```

2. **Explicit locking**:
   ```python
   import threading
   client = APIClient()
   lock = threading.Lock()

   with lock:
       result = client.get_user("123")
   ```

3. **Sequential execution only** (simple but limited)

### Usage

Works in both sync and async contexts:

- **Sync**: `result = client.get_user("123")`
- **Async**: `result = await client.get_user("123")`
```

---

## Scenario B2: Sync Lib → Future Async

**Example**: Legacy library preparing for async migration

```python
# Current: Sync implementation
class DatabaseClient:
    def query(self, sql: str):
        # Sync implementation using sqlite3
        return self.conn.execute(sql).fetchall()

# Future: Want to migrate to async (aiosqlite) without breaking users
from smartasync import smartasync

class DatabaseClient:
    @smartasync
    async def query(self, sql: str):
        # Async implementation using aiosqlite
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(sql)
            return await cursor.fetchall()

# Old code still works!
db = DatabaseClient()
results = db.query("SELECT * FROM users")  # No await needed

# New async code works too!
async def main():
    db = DatabaseClient()
    results = await db.query("SELECT * FROM users")
```

### Impact Analysis

| Issue | Impact | Severity | Details |
|-------|--------|----------|---------|
| **#1** (_sync_mode) | 🟢 MINOR | LOW | Not needed for migration scenario |
| **#2** (Thread safety) | 🔴 BLOCKING | HIGH | **Problem**: Existing users may rely on thread-safety of old sync version!<br>**Impact**: Migration breaks existing thread-safe code<br>**Mitigation**: Require major version bump + clear breaking change notice |
| **#3** (Tests) | 🟡 DEGRADED | MEDIUM | Can't fully test migration path |
| **#4** (Docs) | 🔴 BLOCKING | HIGH | **Problem**: Migration guide doesn't exist<br>**Impact**: Users don't know this is possible |

### Recommendations

❌ **NOT RECOMMENDED** for migration without careful planning

**Critical issue**: Issue #2 makes this a **BREAKING CHANGE** if old code was thread-safe.

### Migration Checklist

If you still want to use SmartAsync for migration:

```markdown
## Migration Guide Template

### Version X.0.0 - Breaking Changes

#### Thread Safety

⚠️ **BREAKING**: This version is **not thread-safe** due to SmartAsync adoption.

**Before** (v1.x - thread-safe):
```python
db = DatabaseClient()

def worker():
    results = db.query("SELECT * FROM users")  # ✅ Thread-safe

threads = [threading.Thread(target=worker) for _ in range(10)]
# All threads could share 'db' instance
```

**After** (v2.0.0 - not thread-safe):
```python
# ❌ BROKEN: Shared instance
db = DatabaseClient()

# ✅ FIX: Per-thread instances
import threading
thread_local = threading.local()

def worker():
    if not hasattr(thread_local, 'db'):
        thread_local.db = DatabaseClient()
    results = thread_local.db.query("SELECT * FROM users")
```

#### Async Support (NEW)

✅ Now supports async contexts:

```python
async def main():
    db = DatabaseClient()
    results = await db.query("SELECT * FROM users")
```
```

---

## Cross-Scenario Patterns

### Pattern 1: Thread Safety Mitigation

**Affected scenarios**: A1 (multi-threaded), A4 (parallel tests), B1 (library users), B2 (migration)

**Universal solution**: Thread-local storage

```python
import threading

# Global thread-local storage
_thread_local = threading.local()

def get_instance(cls, *args, **kwargs):
    """Get or create thread-local instance."""
    attr_name = f'_{cls.__name__}_instance'
    if not hasattr(_thread_local, attr_name):
        setattr(_thread_local, attr_name, cls(*args, **kwargs))
    return getattr(_thread_local, attr_name)

# Usage
client = get_instance(APIClient, api_key="...")
result = client.fetch("...")
```

---

### Pattern 2: Test Isolation

**Affected scenarios**: A3 (dual-mode), A4 (testing)

**Universal solution**: pytest fixture with cache reset

```python
import pytest

@pytest.fixture(autouse=True)
def isolate_smartasync():
    """Isolate SmartAsync cache between tests."""
    # Reset all registered caches
    from smartasync import _reset_all_caches  # Would need to implement
    _reset_all_caches()
    yield
```

---

### Pattern 3: Explicit Mode Control (When Issue #1 Fixed)

**All scenarios benefit** from explicit mode control:

```python
# When Issue #1 is fixed
from smartasync import SmartAsync, smartasync

class APIClient(SmartAsync):
    def __init__(self, mode: str = 'auto'):
        """
        mode: 'auto' (detect), 'sync' (force sync), 'async' (force async)
        """
        sync_mode = (mode == 'sync')
        SmartAsync.__init__(self, _sync=sync_mode)

    @smartasync
    async def fetch(self, url: str):
        ...

# Usage
client_sync = APIClient(mode='sync')    # Always sync
client_async = APIClient(mode='async')  # Always async
client_auto = APIClient(mode='auto')    # Auto-detect (current behavior)
```

---

## Priority Matrix: Issues × Scenarios

| Scenario | Issue #1 Priority | Issue #2 Priority | Issue #3 Priority | Issue #4 Priority |
|----------|------------------|------------------|------------------|------------------|
| **A1** (Sync→Async) | LOW | MEDIUM | LOW | MEDIUM |
| **A2** (Async→Sync) | LOW | LOW | LOW | MEDIUM |
| **A3** (Dual-mode) | MEDIUM | LOW | MEDIUM | **CRITICAL** |
| **A4** (Testing) | MEDIUM | MEDIUM | **CRITICAL** | MEDIUM |
| **B1** (Lib author) | MEDIUM | **CRITICAL** | MEDIUM | **CRITICAL** |
| **B2** (Migration) | LOW | **CRITICAL** | MEDIUM | **CRITICAL** |

### Overall Priority

1. **Issue #4** (Documentation): CRITICAL for A3, B1, B2
2. **Issue #2** (Thread safety): CRITICAL for B1, B2
3. **Issue #3** (Tests): CRITICAL for A4
4. **Issue #1** (_sync_mode): MEDIUM across all

---

## Recommendations by Scenario

### ✅ Recommended Uses (Low Risk)

| Scenario | Risk Level | Conditions |
|----------|-----------|------------|
| **A2** (Async→Sync) | 🟢 LOW | Single-threaded async framework |
| **A3** (Dual-mode) | 🟢 LOW | Separate CLI/API processes |
| **A1** (Sync→Async) | 🟡 MEDIUM | Single-threaded or per-thread instances |

### ⚠️ Use with Caution (Medium Risk)

| Scenario | Risk Level | Conditions |
|----------|-----------|------------|
| **A4** (Testing) | 🟡 MEDIUM | Sequential tests or cache reset |
| **A1** (Sync→Async) | 🟡 MEDIUM | Multi-threaded (with mitigations) |

### ❌ Not Recommended (High Risk)

| Scenario | Risk Level | Reason |
|----------|-----------|--------|
| **B1** (Lib author) | 🔴 HIGH | Thread safety issues affect all users |
| **B2** (Migration) | 🔴 HIGH | Breaking change for thread-safe code |

**Exception**: B1 and B2 become MEDIUM risk after Issue #2 is resolved or clearly documented with mitigations.

---

## Roadmap Impact

### v0.1.1 (Hotfix)

- **Fix Issue #4**: Add "When to Use" section
  - **Impact**: A3, B1, B2 become discoverable

- **Fix Issue #1**: Make `_sync_mode` functional
  - **Impact**: A3, A4 gain explicit control

### v0.1.2 (Testing)

- **Fix Issue #3**: Add edge case tests
  - **Impact**: A4 gains confidence

### v0.2.0 (Optional Thread Safety)

- **Address Issue #2**: Optional thread-safe mode
  - **Impact**: B1, B2 become recommended
  - **Trade-off**: Performance overhead (~0.1μs per call)

---

## Conclusion

**SmartAsync is best suited for**:
1. ✅ **Dual-mode frameworks** (A3) - Primary use case
2. ✅ **Async apps calling sync libs** (A2) - Low risk
3. ⚠️ **Sync apps calling async libs** (A1) - Medium risk (thread safety)

**Not recommended for** (until Issue #2 resolved):
1. ❌ **Public libraries** (B1) - Users may be multi-threaded
2. ❌ **Migration path** (B2) - May break thread-safe code

**Critical fixes needed**:
- Issue #4 (docs) - Prevents discovery
- Issue #2 (thread safety) - Blocks library use cases

---

**Date**: 2025-11-10
**Reviewer**: Scenario Analysis Team
**Next Review**: After v0.1.1 release
