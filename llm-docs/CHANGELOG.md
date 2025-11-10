# SmartAsync - Version History (LLM Format)

Structured changelog for LLM consumption. Focuses on API changes, breaking changes, and feature additions.

---

## v0.1.1 - LLM Documentation (2025-11-10)

**Status**: Alpha (Development Status :: 3 - Alpha)

### Documentation

**LLM-optimized documentation** added in `llm-docs/` directory:
- ✅ QUICKSTART.md - 30-second guide (~60 lines)
- ✅ API.yaml - Structured API reference (~200 lines)
- ✅ PATTERNS.md - 8 usage patterns + anti-pattern (~150 lines)
- ✅ EXAMPLES.md - 9 complete working examples (~440 lines)
- ✅ CHANGELOG.md - Version history for LLMs (~180 lines)
- ✅ README.md - LLM docs overview (~120 lines)

**Token reduction**: ~60% compared to human documentation (1231 lines LLM vs. 2500+ lines human docs)

**Badge added**: Purple "LLM Docs" badge in main README

### API Changes

**None** - Documentation-only release.

### Breaking Changes

**None** - Backward compatible.

---

## v0.1.0 - Initial Release (2025-11-10)

**Status**: Alpha (Development Status :: 3 - Alpha)

### Core Features

**Bidirectional async/sync support**:
- ✅ Async methods work in sync contexts (via `asyncio.run()`)
- ✅ Sync methods work in async contexts (via `asyncio.to_thread()`)
- ✅ Async methods work in async contexts (native coroutines)
- ✅ Sync methods work in sync contexts (pass-through)

**Decorator**: `@smartasync`
- Signature: `smartasync(func: Callable) -> Callable`
- Returns: Wrapped function with context detection
- Usage: Apply to any method (sync or async)

**Implementation details**:
- Context detection: `asyncio.get_running_loop()` with RuntimeError catch
- Asymmetric caching: True (async) cached, False (sync) always rechecked
- Dispatch: Pattern matching (Python 3.10+ match/case)
- Cache reset: `method._smartasync_reset_cache()` for testing

**Compatibility**:
- ✅ `__slots__` classes supported
- ✅ Bound methods (class instances)
- ✅ Error propagation (exceptions preserved)
- ✅ Thread-safe (decorator registration and runtime)

### Performance Characteristics

| Operation | Overhead | Context |
|-----------|----------|---------|
| Sync context + async method | ~102μs | `asyncio.run()` dominates |
| Async context + async method (first) | ~2.3μs | Context detection |
| Async context + async method (cached) | ~1.3μs | Cache hit |
| Async context + sync method | ~50-100μs | Thread offload |

**Conclusion**: Negligible overhead for I/O-bound operations (network, database, file I/O).

### Test Coverage

**10 tests**, 97% coverage:
- `test_sync_context`: Async method in sync context
- `test_async_context`: Async method in async context + sync method offload
- `test_slots`: `__slots__` compatibility (sync)
- `test_slots_async`: `__slots__` compatibility (async)
- `test_cache_reset`: Cache reset functionality
- `test_error_propagation`: Error handling (sync)
- `test_error_propagation_async`: Error handling (async)
- `test_cache_shared_between_instances`: Per-method cache behavior
- `test_sync_to_async_transition`: Context transition behavior
- `test_bidirectional_scenario_a2`: Async app calling sync library

### Dependencies

**Zero external dependencies** - stdlib only:
- `asyncio` (built-in)
- `functools` (built-in)
- `inspect` (built-in)

### Known Limitations

**By design**:
- Asymmetric caching (sync context always rechecked) → ~2μs overhead per sync call
- `asyncio.run()` overhead (~100μs) for sync→async transition
- Cannot transition async→sync within same event loop

**Python requirements**:
- Python 3.10+ (uses pattern matching)

### Use Cases Supported

**Primary** (recommended):
1. CLI tools using async libraries (httpx, aiohttp)
2. Async web apps (FastAPI, aiohttp) using sync legacy libraries (sqlite3, requests)
3. Testing async code without pytest-asyncio
4. Unified library APIs (single codebase, both contexts)

**Secondary**:
5. Gradual async migration (mixed sync/async codebase)
6. Plugin systems (plugins can be sync or async)
7. Mixed frameworks (Jupyter notebooks, Django with async views)

**Not recommended**:
- High-frequency pure sync calls (use plain sync)
- CPU-bound operations (use multiprocessing)
- Existing pure async codebases (no benefit)

### Breaking Changes

**None** - initial release.

### Deprecations

**None** - initial release.

---

## Future Versions

### Planned for v0.2.0 (tentative)

**Under consideration**:
- Optional custom executor for thread offload
- Logging/debugging mode for dispatch decisions
- Type stubs for better IDE support
- Performance optimizations for cached path

**Not planned**:
- Alternative context detection methods (current approach is correct)
- Symmetric caching (breaks correctness)
- External dependencies (maintain zero-dependency status)

---

## Version History Format

Each version entry contains:
- **Status**: Development status classifier
- **Core Features**: New functionality with test references
- **Performance**: Measured overhead changes
- **Test Coverage**: New tests and coverage percentage
- **Dependencies**: Changes to requirements
- **Breaking Changes**: API incompatibilities
- **Deprecations**: Features marked for removal
- **Known Limitations**: Design trade-offs

---

## References

- **Source code**: `src/smartasync/core.py`
- **Tests**: `tests/test_smartasync.py`
- **Human docs**: `docs/`
- **LLM docs**: `llm-docs/`

---

**Last Updated**: 2025-11-10
**Format Version**: 1.0 (LLM-optimized)
