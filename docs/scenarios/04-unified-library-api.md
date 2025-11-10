# Scenario 04: Unified Library API

**Target Audience**: Library authors, open source maintainers
**Difficulty**: Intermediate
**Keywords**: library design, API design, async library, dual interface

---

## 📋 The Problem

Library authors face a difficult choice:

**Option 1: Sync-only API**
- Easy to use for beginners
- Works in any context
- But blocks event loop in async apps
- Misses async performance benefits

**Option 2: Async-only API**
- Non-blocking, efficient
- Great for async apps
- But requires `asyncio.run()` boilerplate for CLI/sync usage
- Excludes sync-only users

**Option 3: Dual APIs (both sync and async)**
- Maintain two implementations
- Double the testing surface
- Risk of behavior divergence
- Confusing for users (which one to use?)

Common examples:
- HTTP clients (requests vs httpx/aiohttp)
- Database drivers (psycopg2 vs asyncpg)
- Cloud SDK clients

---

## 💡 Solution with SmartAsync

**Single implementation, dual interface**:

- Write one async implementation
- Users can call it sync or async
- No duplicate code
- Consistent behavior
- Automatic adaptation to context

**Pattern**:
```
Library with @smartasync methods
├─→ CLI users: call without await
├─→ Script users: call without await
├─→ Async app users: call with await
└─→ Async lib users: call with await
```

---

## 🎯 When to Use

**Ideal for**:
- New libraries targeting broad audience
- HTTP/API clients
- Data processing libraries
- Developer tools and utilities
- Configuration management libraries

**Perfect when**:
- You want maximum user adoption
- Users span sync and async codebases
- You don't want to maintain two APIs
- Behavior should be identical in both modes

---

## ⚠️ Considerations

### Design Decisions

**Performance expectations**:
- Sync calls: ~100μs overhead from asyncio.run()
- Usually negligible compared to I/O operations
- Document this for performance-critical users

**API documentation**:
- Show both usage patterns in docs
- Make it clear the same method works both ways
- Provide migration guides from sync-only libs

**Semantic versioning**:
- Adding SmartAsync to existing async-only API: minor version bump
- Users can adopt gradually (no breaking change)

### When NOT to Use

**Avoid if**:
- Library is performance-critical (nanosecond-level)
- You need different sync/async behavior
- Target audience is async-only (no benefit)
- You want explicit control over thread pools

**Alternatives**:
- Separate sync/async packages (like requests/httpx)
- Async-only with examples of asyncio.run() usage
- Wrapper package pattern (thin sync wrapper over async core)

---

## 🔗 Related Scenarios

- **01: CLI Tools** - Consumers of unified APIs
- **05: Gradual Migration** - Transitioning existing APIs
- **06: Plugin Systems** - Accepting both sync and async implementations

---

## 📚 Real-World Examples

Libraries that could benefit:
- **httpx** - Already async-first, could add sync mode
- **boto3** - AWS SDK (currently sync-only)
- **stripe-python** - Payment API (currently sync-only)
- **openai-python** - AI API client

---

## 🎯 Success Metrics

Your unified library API is successful when:
- Users don't need to know about async/sync distinction
- No "sync" vs "async" in method names
- Single import works for everyone
- Issue tracker shows diverse usage patterns
- Both sync and async users are happy

---

**Next Steps**:
- See [05: Gradual Migration](05-gradual-migration.md) for transitioning existing libraries
- Check [06: Plugin Systems](06-plugin-systems.md) for accepting plugins
