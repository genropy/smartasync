# SmartAsync - Technical Report

**Version**: 0.1.0
**Date**: 2025-11-10
**Status**: Alpha - Ready for target use cases with known limitations

---

## Executive Summary

**SmartAsync** is a decorator that enables writing async methods once and calling them in both sync and async contexts through automatic context detection. It's designed specifically for **CLI + HTTP API frameworks** (like smpub), **testing**, and **CLI tools** that use async libraries internally.

**Verdict**: ✅ **Production-ready for target use cases** with clear documentation of limitations.

**Key Strengths**:
- Zero configuration required
- Solves real problem (code duplication in CLI+API)
- Negligible performance overhead for target scenarios
- Simple, maintainable implementation

**Key Limitations**:
- Not thread-safe (by design)
- `_sync_mode` parameter currently non-functional (Issue #1)
- Per-method caching can be problematic in mixed contexts

---

## Design Overview

### How It Works

```python
@smartasync
async def fetch_data(self, url: str):
    async with httpx.AsyncClient() as client:
        return await client.get(url).json()

# Sync context (CLI)
result = obj.fetch_data("https://api.example.com")  # No await!

# Async context (web server)
result = await obj.fetch_data("https://api.example.com")  # Await!
```

**Mechanism**:
1. Decorator wraps async method
2. At runtime, checks for running event loop via `asyncio.get_running_loop()`
3. **Async context** (loop found): Returns coroutine (must await)
4. **Sync context** (no loop): Executes with `asyncio.run()` and returns result

### Asymmetric Caching Strategy

- **Async detected** → Cache = True forever (can't go back to sync)
- **Sync detected** → Cache = False, recheck every time (can transition to async)

**Rationale**: Correct behavior (async→sync transition is impossible), while allowing sync→async transition.

---

## Performance Analysis

### Measurements

| Context | First Call | Cached | Impact |
|---------|-----------|--------|--------|
| Decoration | 3-4μs | - | One-time cost |
| Sync context | ~102μs | N/A | Dominated by `asyncio.run()` |
| Async (first) | ~2.3μs | - | Detection overhead |
| Async (cached) | ~1.3μs | ~1.3μs | Minimal overhead |

### Real-World Impact

**CLI Tools**:
- Typical I/O: 100-1000ms
- SmartAsync overhead: 0.1ms
- **Impact**: 0.01-0.1% → **Negligible**

**Web APIs**:
- Typical latency: 10-200ms
- SmartAsync overhead: 0.002ms (cached)
- **Impact**: 0.001-0.02% → **Negligible**

**Conclusion**: Performance overhead is acceptable for all target use cases.

---

## Known Issues and Limitations

### Issue #1: `_sync_mode` Parameter Ignored (BUG)

**Severity**: 🔴 HIGH
**Status**: [GitHub Issue #1](https://github.com/genropy/smartasync/issues/1)

**Problem**: The `SmartAsync` class accepts `_sync_mode` parameter that should force sync/async behavior, but the `@smartasync` decorator ignores it completely.

```python
# Currently broken
obj = MyClass(_sync=True)  # User requests sync mode
result = obj.my_method()   # Still returns coroutine in async context!
```

**Fix Required**: Decorator must check `self._sync_mode` before auto-detection.

**Workaround**: Don't use `_sync_mode` parameter; rely on auto-detection.

---

### Issue #2: Not Thread-Safe (DESIGN LIMITATION)

**Severity**: 🟡 MEDIUM
**Status**: [GitHub Issue #2](https://github.com/genropy/smartasync/issues/2)

**Problem**: Cache access has no thread synchronization, causing race conditions in multi-threaded scenarios.

**When it's a problem**:
- ❌ Concurrent multi-threading with shared instances
- ❌ Mixed sync/async contexts in different threads

**When it's NOT a problem** (target use cases):
- ✅ Single-threaded async (event loop)
- ✅ Single-threaded sync (CLI)
- ✅ Web servers (request isolation)

**Decision**: Document limitation rather than add locks (zero overhead for target scenarios).

---

### Issue #3: Per-Method Caching

**Severity**: 🟡 MEDIUM
**Status**: Documented in [GitHub Issue #2](https://github.com/genropy/smartasync/issues/2)

**Behavior**: Cache is shared across **all instances** of the same class (per-method, not per-instance).

```python
api1 = API()
api2 = API()

# api1 called in async context
asyncio.run(async_call(api1))  # Sets cache = True

# api2 uses same cache!
api2.call()  # Returns coroutine (cache says async context)
```

**When it's a problem**:
- ❌ Mixed sync/async in same process (rare)
- ❌ Web server + background sync workers (same process)

**When it's NOT a problem**:
- ✅ CLI (always sync across all instances)
- ✅ Web server (always async across all instances)
- ✅ Testing (contexts usually separated)

**Workaround**: Use separate processes or explicit instance-based caching (future enhancement).

---

## Target Use Cases

### ✅ Perfect For

#### 1. CLI + HTTP API Frameworks (Primary Use Case)

**Example**: smpub framework

```python
from smartasync import smartasync
from smpub import PublishedClass, ApiSwitcher

class DataHandler(PublishedClass):
    api = ApiSwitcher()

    @api
    @smartasync
    async def process_data(self, input_file: str):
        async with aiofiles.open(input_file) as f:
            data = await f.read()
        return await self._process(data)

# CLI: python cli.py process data.csv
# → Calls process_data() synchronously

# API: POST /process {"file": "data.csv"}
# → Calls process_data() asynchronously
```

**Benefits**:
- Zero code duplication
- Single source of truth
- Automatic context detection

---

#### 2. Testing (Sync + Async)

```python
# Fast unit tests (sync)
def test_process_data():
    handler = DataHandler()
    result = handler.process_data("test.csv")
    assert result.status == "ok"

# Integration tests (async)
@pytest.mark.asyncio
async def test_process_data_with_real_io():
    handler = DataHandler()
    result = await handler.process_data("test.csv")
    assert result.status == "ok"
```

**Benefits**:
- Test flexibility
- Fast unit tests (no event loop overhead)
- Realistic integration tests

---

#### 3. CLI Tools Using Async Libraries

```python
class GitHubCLI:
    @smartasync
    async def fetch_repo(self, name: str):
        async with httpx.AsyncClient() as client:
            return await client.get(f"https://api.github.com/repos/{name}")

# CLI usage (looks synchronous to user)
cli = GitHubCLI()
repo = cli.fetch_repo("anthropics/claude-code")
print(repo.json())
```

**Benefits**:
- Use modern async libraries (httpx, aiofiles, etc.)
- Present clean sync interface to CLI users
- No need for separate sync wrappers

---

### ⚠️ Use With Caution

1. **Long-running services with context transitions**: Cache may cause unexpected behavior
2. **Multi-threading**: No thread-safety guarantees
3. **High-frequency loops**: `asyncio.run()` overhead adds up in tight sync loops

---

### ❌ Not Recommended For

1. **Mixed sync/async in same process**
   - Example: Web server + background sync workers
   - Issue: Shared cache causes conflicts
   - Workaround: Separate processes

2. **Heavy multi-threading**
   - Issue: Race conditions in cache
   - Workaround: Per-thread instances or locks

3. **Microsecond-level performance**
   - Issue: `asyncio.run()` adds ~100μs per sync call
   - Alternative: Explicit sync/async methods

---

## Testing Status

### Current Coverage

- **Line coverage**: 89%
- **Branch coverage**: Good for happy paths
- **Edge case coverage**: Limited (see Issue #3)

### Test Categories

✅ **Implemented**:
- Sync context detection
- Async context detection
- `__slots__` compatibility
- Cache reset functionality
- Mixed sync/async methods

⚠️ **Missing** (Issue #3):
- `_sync_mode` enforcement (when fixed)
- Cache pollution between instances
- Thread safety scenarios
- Error propagation edge cases
- Repeated context transitions

---

## Comparison with Alternatives

### Alternative 1: Separate sync/async methods

```python
async def fetch_async(self):
    """Async version."""
    ...

def fetch_sync(self):
    """Sync wrapper."""
    return asyncio.run(self.fetch_async())
```

**Pros**:
- ✅ Explicit, clear intent
- ✅ No magic, no cache
- ✅ Thread-safe

**Cons**:
- ❌ Code duplication
- ❌ Maintenance burden (keep in sync)
- ❌ User must choose correct method

**SmartAsync wins for**: CLI+API frameworks, testing

---

### Alternative 2: Explicit mode parameter

```python
api = API(mode='sync')  # or mode='async'
```

**Pros**:
- ✅ User controls behavior
- ✅ Predictable
- ✅ No auto-detection issues

**Cons**:
- ❌ Must decide upfront
- ❌ Less flexible for testing

**SmartAsync wins for**: Zero-configuration scenarios

---

## Roadmap

### v0.1.1 (Bug Fixes)

- [x] Create GitHub issues
- [ ] Fix Issue #1: Make `_sync_mode` functional
- [ ] Add "When to Use" section to README (Issue #4)
- [ ] Document thread safety limitations

### v0.1.2 (Testing)

- [ ] Add edge case tests (Issue #3)
- [ ] Document cache behavior more clearly
- [ ] Add examples for common patterns

### v0.2.0 (Enhancements)

- [ ] Optional per-instance caching mode
- [ ] Optional thread-safety mode (with locks)
- [ ] Performance benchmarks in documentation

---

## Recommendations

### For Users

1. **Read "When to Use" section** before adopting
2. **Stick to target use cases** (CLI+API, testing)
3. **Don't use in multi-threaded scenarios** without understanding limitations
4. **Use explicit sync/async methods** if you need predictability

### For Maintainers

1. **Fix Issue #1** (HIGH priority) - `_sync_mode` must work
2. **Document limitations clearly** (Issue #4)
3. **Add edge case tests** (Issue #3)
4. **Keep implementation simple** - complexity is the enemy

---

## Conclusion

**SmartAsync is a specialized tool** that solves a real problem (code duplication in CLI+API frameworks) with acceptable trade-offs.

**Strengths**:
- ✅ Zero configuration
- ✅ Solves real problem elegantly
- ✅ Good performance for target use cases
- ✅ Simple implementation

**Weaknesses**:
- ⚠️ `_sync_mode` currently broken (fixable)
- ⚠️ Not thread-safe (by design)
- ⚠️ Per-method caching has edge cases (documented)

**Final Verdict**: ✅ **SHIP IT** for target use cases (CLI+API, testing) with:
1. Fix for Issue #1
2. Clear documentation of limitations
3. Examples of appropriate usage

**Not a silver bullet**, but a **useful specialist** for specific scenarios.

---

**Author**: Genropy Team
**Reviewers**: Technical Analysis Team
**Date**: 2025-11-10
**Next Review**: After v0.1.1 release
