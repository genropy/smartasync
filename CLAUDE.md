# Claude Code Instructions - SmartAsync

## Project Context

**SmartAsync** is a unified sync/async API decorator that automatically detects execution context and adapts method behavior accordingly.

### Current Status
- **Development Status**: Alpha (`Development Status :: 3 - Alpha`)
- **Version**: 0.1.0
- **Has Implementation**: Complete (core functionality implemented and tested)
- **Dependencies**: None (pure Python, stdlib only)

### Project Overview

SmartAsync provides:
- `@smartasync` decorator for automatic sync/async context detection
- `SmartAsync` base class for instance-level sync mode control
- Asymmetric caching for optimal performance
- Compatible with `__slots__` for memory efficiency

## Repository Information

- **Owner**: genropy
- **Repository**: https://github.com/genropy/smartasync
- **Documentation**: https://smartasync.readthedocs.io (planned)
- **License**: MIT
- **Part of**: Genro-Libs toolkit

## Project Structure

```
smartasync/
├── src/smartasync/
│   ├── __init__.py          # Package exports
│   └── core.py              # SmartAsync and smartasync implementation
├── tests/
│   └── test_smartasync.py    # Complete test suite
├── docs/                    # Documentation (to be added)
├── pyproject.toml          # Package configuration
├── README.md               # Project overview
├── LICENSE                 # MIT license
└── CLAUDE.md               # This file
```

## Language Policy

- **Code, comments, and commit messages**: English
- **Documentation**: English (primary)
- **Communication with user**: Italian (per user preference)

## Git Commit Policy

- **NEVER** include Claude as co-author in commits
- **ALWAYS** remove "Co-Authored-By: Claude <noreply@anthropic.com>" line
- Use conventional commit messages following project style

## Development Guidelines

### Core Principles

1. **Zero dependencies**: Only use Python stdlib
2. **Automatic detection**: No manual configuration required
3. **Performance conscious**: Minimize overhead while maintaining correctness
4. **`__slots__` compatible**: Work with memory-optimized classes

### Testing

Complete test suite in `tests/test_smartasync.py`:
- Sync context tests (no event loop)
- Async context tests (with event loop)
- `__slots__` compatibility tests
- Cache management tests
- Mixed sync/async tests

### Known Design Decisions

1. **Asymmetric caching**: Cache True (async) forever, always recheck False (sync)
   - **Why**: Correct behavior (can't transition async → sync)
   - **Trade-off**: ~2 microseconds overhead per sync call

2. **SmartAsync base class with `__slots__`**: Provides instance-level control
   - **Why**: Allows `_sync_mode` storage without breaking `__slots__` in subclasses

3. **`asyncio.run()` for sync context**: Simple and reliable
   - **Why**: Works everywhere, no need for loop management
   - **Trade-off**: ~100 microseconds overhead (acceptable for CLI/single calls)

## Relationship with Other Projects

SmartAsync is used by:
- **smpub**: For automatic async handler support in ApiSwitcher
- Potentially others in Genro-Libs ecosystem

## Development Workflow

**MANDATORY sequence before every push:**

1. **Run pytest locally**
   ```bash
   pytest
   ```

2. **Run ruff locally**
   ```bash
   ruff check .
   ```

3. **Push only if both pass**
   ```bash
   git push origin main
   ```

**CRITICAL RULES:**
- ❌ **NEVER use `--no-verify`** without explicit user authorization
- ✅ **ALWAYS investigate** failures instead of bypassing
- ✅ Local testing is FAST (seconds) vs CI is SLOW (minutes)

## Performance Characteristics

- **Decoration time**: ~3-4 microseconds (one-time cost)
- **Sync context**: ~102 microseconds (dominated by `asyncio.run()`)
- **Async context (first)**: ~2.3 microseconds
- **Async context (cached)**: ~1.3 microseconds

**Impact**: Negligible for CLI tools and web APIs (0.001-1% overhead)

## Mistakes to Avoid

❌ **DON'T**:
- Add external dependencies
- Cache sync context (False) - breaks correctness
- Skip context detection - always check
- Break `__slots__` compatibility

✅ **DO**:
- Keep implementation simple and correct
- Test both sync and async contexts
- Maintain zero-dependency status
- Preserve asymmetric caching behavior

## Quick Reference

| File | Purpose |
|------|---------|
| core.py | SmartAsync class and smartasync decorator |
| test_smartasync.py | Complete test suite |
| __init__.py | Package exports |

---

**Author**: Genropy Team
**License**: MIT
**Python**: 3.10+
**Part of**: Genro-Libs toolkit
