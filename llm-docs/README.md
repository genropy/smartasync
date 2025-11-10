# SmartAsync - LLM Documentation

This directory contains **LLM-optimized documentation** for SmartAsync, designed for efficient consumption by Large Language Models.

## Why LLM Docs?

Traditional human documentation is:
- **Verbose**: 3-5x longer than necessary for LLMs
- **Narrative**: Prose and storytelling vs. structured data
- **Inefficient**: 60% context/motivation, 40% technical information

**LLM docs achieve 60-75% token reduction** through:
- Dense, structured format (YAML for API reference)
- No redundant explanations
- Direct test references (no hallucination)
- Examples extracted from actual tests

## File Structure

| File | Purpose | Size | Content |
|------|---------|------|---------|
| **QUICKSTART.md** | 30-second guide | ~60 lines | Core concept + basic usage |
| **API.yaml** | Complete API reference | ~200 lines | Structured, machine-readable |
| **PATTERNS.md** | Common usage patterns | ~150 lines | 8 patterns + anti-patterns |
| **EXAMPLES.md** | Working code examples | ~440 lines | 9 complete examples from tests |
| **CHANGELOG.md** | Version history | ~180 lines | API changes, features, breaking changes |

**Total**: ~1030 lines (LLM docs) vs. ~2500+ lines (human docs) → **~60% reduction**

## Quick Navigation

### For Quick Understanding
Start with: **QUICKSTART.md** (30 seconds to understand SmartAsync)

### For API Reference
Go to: **API.yaml** (complete structured reference)

### For Common Use Cases
Read: **PATTERNS.md** (8 patterns extracted from tests)

### For Complete Examples
See: **EXAMPLES.md** (9 runnable examples with test references)

### For Version Changes
Check: **CHANGELOG.md** (v0.1.0 feature list)

## Key Features (Quick Reference)

**What it does**: Bidirectional decorator for methods working in both sync and async contexts

**Core behavior**:
- Async method in sync context → `asyncio.run()`
- Sync method in async context → `asyncio.to_thread()`
- Async method in async context → native coroutine
- Sync method in sync context → pass-through

**Performance**: ~1-2μs (async cached), ~100μs (sync context), ~50-100μs (thread offload)

**Dependencies**: None (stdlib only)

**Python**: 3.10+ (uses pattern matching)

**Test coverage**: 97% (10 tests)

## Usage Pattern

```python
from smartasync import smartasync

class Service:
    @smartasync
    async def fetch(self, url: str) -> dict:
        async with httpx.AsyncClient() as client:
            return await client.get(url)

# Sync context (CLI, scripts)
svc = Service()
data = svc.fetch("https://api.example.com")  # No await!

# Async context (FastAPI, aiohttp)
async def handler():
    svc = Service()
    data = await svc.fetch("https://api.example.com")  # With await
```

## Source of Truth

All examples are extracted from **tests/test_smartasync.py** (391 lines, 10 tests, 97% coverage).

Every example has explicit test reference:
```markdown
**From**: tests/test_smartasync.py::test_sync_context
```

**No hallucination** - all features are tested and documented.

## Maintenance

LLM docs are synchronized with:
- **Source code**: `src/smartasync/core.py`
- **Tests**: `tests/test_smartasync.py`
- **Human docs**: `docs/`

When updating SmartAsync:
1. Update tests first
2. Update implementation
3. Regenerate LLM docs from tests
4. Update human docs

## Validation

LLM docs should:
- ✅ Have test references for all examples
- ✅ Be runnable (copy-paste works)
- ✅ Match actual behavior (no invented features)
- ✅ Use structured format (YAML for API)
- ✅ Be dense (no redundant prose)

## Related Documentation

| Type | Location | Audience | Format |
|------|----------|----------|--------|
| LLM docs | `llm-docs/` | LLMs, quick reference | Dense, structured |
| Human docs | `docs/` | Developers | Narrative, tutorials |
| Source code | `src/smartasync/` | Maintainers | Python |
| Tests | `tests/` | Verification | pytest |

## Strategy Reference

Based on LLM documentation strategy:
- Location: `/Users/gporcari/Sviluppo/genro_ng/llmdocs/`
- Documents: `LLM-DOCUMENTATION-STRATEGY.md`, `LLM-DOCS-GENERATION-PROMPTS.md`

---

**Created**: 2025-11-10
**Format Version**: 1.0
**Token Reduction**: ~60% vs. human docs
