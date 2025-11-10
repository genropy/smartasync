# How SmartAsync Works: Calling Async Code from Sync Context

**Audience**: Developers learning async/await patterns
**Level**: Intermediate
**Prerequisites**: Basic understanding of Python async/await syntax

---

## Table of Contents

1. [The Problem We're Solving](#the-problem-were-solving)
2. [Python Async Fundamentals](#python-async-fundamentals)
3. [The SmartAsync Solution](#the-smartasync-solution)
4. [Deep Dive: How the Decorator Works](#deep-dive-how-the-decorator-works)
5. [The Caching Strategy](#the-caching-strategy)
6. [Edge Cases and Design Decisions](#edge-cases-and-design-decisions)
7. [Performance Analysis](#performance-analysis)

---

## The Problem We're Solving

### The Core Challenge

Python has two execution models:

1. **Synchronous (traditional)**: Code executes line by line, blocking until each operation completes
2. **Asynchronous (modern)**: Code can pause and resume, allowing concurrent operations

**The problem**: These two models don't mix easily.

### Example: Modern Async Library in Sync Code

Many modern Python libraries are async-first (httpx, aiofiles, asyncpg). Using them from synchronous code requires boilerplate:

```python
import asyncio
import httpx

# Async implementation (what you want to write)
async def fetch_data(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Sync code (where you need to call it)
def main():
    # ❌ This doesn't work:
    # data = fetch_data("https://api.example.com")

    # ✅ You must do this:
    data = asyncio.run(fetch_data("https://api.example.com"))
```

**Pain points**:
- Must remember to wrap every async call with `asyncio.run()`
- Can't easily reuse same code in async contexts
- Boilerplate everywhere

### What We Want

```python
@smartasync
async def fetch_data(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Sync context - works without await
data = fetch_data("https://api.example.com")

# Async context - works with await
async def handler():
    data = await fetch_data("https://api.example.com")
```

**Goal**: Write once, call from anywhere (sync or async).

---

## Python Async Fundamentals

Before understanding SmartAsync, you need to understand how Python async works.

### Coroutines: The Building Block

When you define an `async def` function, calling it **doesn't execute the code**. It creates a **coroutine object**:

```python
async def example():
    print("This won't print yet!")
    return 42

# Calling the function creates a coroutine
coro = example()
# ⚠️ Nothing printed! Code hasn't run!

print(type(coro))  # <class 'coroutine'>

# To actually run it, you need to await it or use asyncio.run()
result = asyncio.run(coro)  # NOW it prints and executes
print(result)  # 42
```

**Key insight**: A coroutine is like a "recipe" or "promise of execution", not the execution itself.

### The Event Loop

Async code requires an **event loop** - a scheduler that manages coroutine execution:

```python
# Event loop lifecycle
loop = asyncio.new_event_loop()      # Create loop
asyncio.set_event_loop(loop)         # Set as current
result = loop.run_until_complete(coro)  # Run coroutine
loop.close()                         # Clean up

# asyncio.run() does all this for you!
result = asyncio.run(coro)
```

### Detecting the Context

Python provides `asyncio.get_running_loop()` to check if an event loop is active:

```python
# In sync context (no loop)
try:
    loop = asyncio.get_running_loop()
    print("In async context")
except RuntimeError:
    print("In sync context")  # This prints

# In async context (loop exists)
async def check():
    try:
        loop = asyncio.get_running_loop()
        print("In async context")  # This prints
    except RuntimeError:
        print("In sync context")

asyncio.run(check())
```

**This is the key**: SmartAsync uses `get_running_loop()` to detect the execution context.

---

## The SmartAsync Solution

### High-Level Architecture

SmartAsync is a **decorator** that wraps async methods and automatically adapts their behavior:

```python
@smartasync
async def fetch(url):
    # Original async implementation
    ...

# Under the hood, SmartAsync creates:
def wrapper(*args, **kwargs):
    coro = fetch(*args, **kwargs)  # Create coroutine

    if <in_async_context>:
        return coro  # Let caller await it
    else:
        return asyncio.run(coro)  # Execute and return result
```

### The Three Execution Paths

SmartAsync has three code paths depending on the context:

```python
@smartasync
async def example():
    return "result"

# Path 1: Sync context (no event loop)
result = example()
# → asyncio.run(coro) → returns "result"

# Path 2: Async context (first call)
async def first_call():
    result = await example()
# → Detects loop → Caches detection → returns coroutine → returns "result"

# Path 3: Async context (subsequent calls)
async def later_call():
    result = await example()
# → Uses cache → returns coroutine immediately → returns "result"
```

---

## Deep Dive: How the Decorator Works

### Step-by-Step Breakdown

Let's examine the decorator implementation with detailed explanations:

```python
def smartasync(method):
    """Decorator that enables calling async methods from sync contexts."""

    # 1. CHECK IF METHOD IS ASYNC
    # Only wrap async methods; sync methods pass through unchanged
    if asyncio.iscoroutinefunction(method):

        # 2. CREATE CACHE VARIABLE
        # Stores whether we've detected async context
        # Lives in the closure (persistent across calls)
        _cached_has_loop = False

        # 3. CREATE WRAPPER FUNCTION
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            nonlocal _cached_has_loop  # Access closure variable

            # 4. CREATE COROUTINE
            # Call the original async method
            # This creates a coroutine object but DOESN'T execute yet
            coro = method(self, *args, **kwargs)

            # 5. CHECK CACHE FIRST (OPTIMIZATION)
            # If we know we're in async context, skip detection
            if _cached_has_loop:
                return coro  # Fast path: return coroutine for await

            # 6. DETECT CONTEXT
            # Try to get the running event loop
            try:
                asyncio.get_running_loop()

                # SUCCESS: Event loop exists → We're in async context
                _cached_has_loop = True  # Cache this discovery
                return coro  # Return coroutine for caller to await

            except RuntimeError:
                # FAILED: No event loop → We're in sync context

                # 7. EXECUTE IN SYNC CONTEXT
                # Create temporary event loop, run coroutine, return result
                try:
                    return asyncio.run(coro)

                except RuntimeError as e:
                    # 8. ERROR HANDLING
                    # Provide helpful error message if user tries to
                    # call sync from within async context incorrectly
                    if "cannot be called from a running event loop" in str(e):
                        raise RuntimeError(
                            f"Cannot call {method.__name__}() synchronously "
                            f"from within an async context. Use "
                            f"'await {method.__name__}()' instead."
                        ) from e
                    raise

        # 9. ADD CACHE RESET (FOR TESTING)
        def reset_cache():
            nonlocal _cached_has_loop
            _cached_has_loop = False

        wrapper._smartasync_reset_cache = reset_cache

        return wrapper
    else:
        # 10. PASS THROUGH SYNC METHODS
        # If method isn't async, don't wrap it
        return method
```

### Execution Flow Diagrams

#### Scenario A: Sync Context (No Event Loop)

```
User calls: obj.fetch(url)
                ↓
    wrapper() is invoked
                ↓
    Create coroutine: coro = method(url)
    (coroutine created but NOT executed)
                ↓
    Check cache: _cached_has_loop == False
                ↓
    Try: asyncio.get_running_loop()
                ↓
    RuntimeError: "no running event loop"
                ↓
    Execute: asyncio.run(coro)
    - Creates new event loop
    - Runs coroutine to completion
    - Returns result
    - Closes loop
                ↓
    Return: "result" (actual value)
                ↓
    User receives: result = "result"
```

#### Scenario B: Async Context (First Call)

```
User calls: await obj.fetch(url)
                ↓
    wrapper() is invoked
                ↓
    Create coroutine: coro = method(url)
    (coroutine created but NOT executed)
                ↓
    Check cache: _cached_has_loop == False
                ↓
    Try: asyncio.get_running_loop()
                ↓
    Success: <asyncio.EventLoop object>
                ↓
    Cache discovery: _cached_has_loop = True
                ↓
    Return: coro (coroutine object)
                ↓
    User awaits: await coro
                ↓
    Coroutine executes in existing event loop
                ↓
    User receives: result = "result"
```

#### Scenario C: Async Context (Subsequent Calls)

```
User calls: await obj.fetch(url)
                ↓
    wrapper() is invoked
                ↓
    Create coroutine: coro = method(url)
                ↓
    Check cache: _cached_has_loop == True  ✨ CACHE HIT
                ↓
    Return: coro (SKIP loop detection!)
                ↓
    User awaits: await coro
                ↓
    User receives: result = "result"

Performance: ~1.3μs vs ~2.3μs (40% faster!)
```

---

## The Caching Strategy

### Why Asymmetric Caching?

SmartAsync uses **asymmetric caching** - it caches only one state (async detected), not the other (sync):

```python
_cached_has_loop = False  # Initial state

# In sync context:
_cached_has_loop = False  # NEVER changes
# → Always rechecks for event loop
# → Always executes with asyncio.run() if no loop

# In async context:
_cached_has_loop = True  # Changes on first call
# → Never rechecks (cache hit every time)
# → Always returns coroutine
```

### Why This Design?

**Problem**: Can you transition between contexts?

```python
# Possible: Sync → Async
obj = MyClass()
result = obj.fetch(url)  # Sync context (no loop)

async def later():
    result = await obj.fetch(url)  # Async context (loop exists) ✅

# Impossible: Async → Sync
async def start():
    result = await obj.fetch(url)  # Async context (loop exists)

result = obj.fetch(url)  # ❌ Can't "unwind" the event loop!
```

**Key insight**: You can **enter** an async context but you can't **exit** it (the event loop keeps running).

### Caching Decision Table

| Cache State | Context | Detection Cost | Action |
|------------|---------|---------------|--------|
| `False` | Sync | ~2μs (check loop) | Execute with `asyncio.run()` |
| `False` | Async | ~2μs (check loop) | Return coro, set cache to `True` |
| `True` | Async | ~0μs (skip check) | Return coro immediately |
| `True` | Sync | Never happens | Loop is still running from before |

**Trade-off**: Sync context has ~2μs overhead on every call, but this is acceptable because:
1. Sync calls are typically one-off (CLI, scripts)
2. 2μs << network latency (10-200ms)
3. Allows transition to async context if needed

---

## Edge Cases and Design Decisions

### Edge Case 1: Nested Event Loops

**Problem**: What if user tries to create nested event loops?

```python
# This will fail:
def sync_wrapper():
    result = asyncio.run(async_method())  # Creates loop 1
    return result

async def outer():
    # This is INSIDE loop 1!
    result = sync_wrapper()  # ❌ Tries to create loop 2 = ERROR!
```

**SmartAsync handling**:

```python
try:
    return asyncio.run(coro)
except RuntimeError as e:
    if "cannot be called from a running event loop" in str(e):
        raise RuntimeError(
            "Cannot call method() synchronously from within async context. "
            "Use 'await method()' instead."
        ) from e
```

**Result**: Clear error message instead of cryptic RuntimeError.

---

### Edge Case 2: Sync Method Decorated

**Problem**: What if you accidentally decorate a sync method?

```python
@smartasync
def sync_method(self):  # Not async!
    return "result"
```

**SmartAsync handling**:

```python
if asyncio.iscoroutinefunction(method):
    # ... wrapping logic ...
else:
    return method  # Pass through unchanged
```

**Result**: No-op. The decorator silently passes through sync methods.

---

### Edge Case 3: Multiple Instances

**Problem**: Is the cache per-instance or per-method?

```python
obj1 = MyClass()
obj2 = MyClass()

# If obj1 called in async context, does it affect obj2?
```

**Answer**: Cache is **per-method**, not per-instance.

**Implication**:

```python
# Thread 1 (async context)
async def worker1():
    result = await obj1.fetch(url)  # Sets cache = True

# Thread 2 (sync context)
def worker2():
    result = obj2.fetch(url)  # ❌ Cache says True, returns coro!
    # User didn't await, so result is a coroutine object = BUG
```

**Solution**: Use per-thread instances (see [Thread Safety Guide](../scenarios/A1-sync-app-async-libs.md#issue-2-not-thread-safe)).

---

### Edge Case 4: Exception in Coroutine

**Problem**: What if the async method raises an exception?

```python
@smartasync
async def buggy_method(self):
    raise ValueError("Something went wrong")

# Sync context
result = buggy_method()  # What happens?
```

**Flow**:

```python
coro = buggy_method()  # Coroutine created (no error yet)
return asyncio.run(coro)  # NOW the exception is raised
```

**Result**: Exception propagates normally. SmartAsync is transparent to exceptions.

---

## Performance Analysis

### Benchmark Results

| Operation | Time | Notes |
|-----------|------|-------|
| Decoration overhead | 3-4μs | One-time cost at import |
| Sync call (no loop) | ~102μs | Dominated by `asyncio.run()` |
| Async call (first) | ~2.3μs | Includes loop detection |
| Async call (cached) | ~1.3μs | Cache hit, no detection |
| Native async call | ~1.1μs | Baseline (no decorator) |

### Overhead Analysis

```python
# Network request (baseline)
await httpx.get(url)  # 10-200ms

# SmartAsync overhead in async context
# 1.3μs / 10,000μs = 0.013% overhead  ← Negligible!

# SmartAsync overhead in sync context
# 102μs / 10,000μs = 1% overhead  ← Still acceptable
```

**Conclusion**: For I/O-bound operations (network, disk), SmartAsync overhead is negligible.

---

### Why `asyncio.run()` is "Expensive"

```python
# What asyncio.run() does internally:
def asyncio_run_simplified(coro):
    # 1. Create new event loop (~50μs)
    loop = asyncio.new_event_loop()

    # 2. Set as current loop (~5μs)
    asyncio.set_event_loop(loop)

    try:
        # 3. Run coroutine (~variable, depends on work)
        result = loop.run_until_complete(coro)
    finally:
        # 4. Cleanup (~45μs)
        loop.close()
        asyncio.set_event_loop(None)

    return result

# Total overhead: ~100μs (even for instant coroutines)
```

**Design decision**: Accept this overhead for sync calls because:
1. Simple and robust (no loop management needed)
2. Only affects sync context (not the common case)
3. Alternative (persistent loop) adds complexity

---

## Visual Summary

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│ User Code                                           │
│                                                     │
│ obj.method()  or  await obj.method()               │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ @smartasync Decorator                               │
│                                                     │
│ 1. Is method async?                                │
│    ├─ No  → Return method unchanged                │
│    └─ Yes → Continue                               │
│                                                     │
│ 2. Create wrapper() function                       │
│    - Has cache: _cached_has_loop = False           │
│    - Checks context on each call                   │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ wrapper() Execution                                 │
│                                                     │
│ 1. Create coroutine: coro = method(...)            │
│                                                     │
│ 2. Check cache                                     │
│    _cached_has_loop == True?                       │
│    ├─ Yes → Return coro (fast path)               │
│    └─ No  → Continue                               │
│                                                     │
│ 3. Detect context: asyncio.get_running_loop()     │
│    ├─ Success → Async context                     │
│    │   ├─ Set cache = True                        │
│    │   └─ Return coro                             │
│    │                                               │
│    └─ RuntimeError → Sync context                 │
│        ├─ Execute: asyncio.run(coro)              │
│        └─ Return result                           │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ User Receives                                       │
│                                                     │
│ Sync context:  result = value (direct)             │
│ Async context: result = await coro → value         │
└─────────────────────────────────────────────────────┘
```

---

## Further Reading

### Related Documentation

- [Scenario A1: Sync App → Async Libs](../scenarios/A1-sync-app-async-libs.md) - Using SmartAsync in sync applications
- [TECH-REPORT.md](../../TECH-REPORT.md) - Complete technical analysis
- [Issue #2: Thread Safety](https://github.com/genropy/smartasync/issues/2) - Thread safety considerations

### Python Async Resources

- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [PEP 492 – Coroutines with async and await syntax](https://peps.python.org/pep-0492/)
- [Real Python: Async IO in Python](https://realpython.com/async-io-python/)

---

## Glossary

| Term | Definition |
|------|------------|
| **Coroutine** | Object created by calling an `async def` function; represents pending execution |
| **Event Loop** | Scheduler that manages execution of coroutines |
| **Sync Context** | Code executing without an active event loop |
| **Async Context** | Code executing within an active event loop |
| **Decorator** | Function that wraps another function to modify its behavior |
| **Closure** | Function that captures variables from its surrounding scope |
| **Cache** | Stored result of a previous computation to avoid repeating work |

---

**Document Version**: 1.0
**Last Updated**: 2025-11-10
**Author**: SmartAsync Documentation Team
**Feedback**: Open an issue on [GitHub](https://github.com/genropy/smartasync/issues)
