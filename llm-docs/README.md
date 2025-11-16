# SmartAsync - LLM Documentation

> **LLM instructions**  
> 1. Read this README completely first.  
> 2. Open additional files *only if the task requires them*:  
>    - `QUICKSTART.md` → onboarding + minimal example  
>    - `API.yaml` → authoritative signatures/behaviors/tests  
>    - `PATTERNS.md` → reusable scenarios  
>    - `EXAMPLES.md` → full snippets (all from tests)  
>    - `CHANGELOG.md` → version history + coverage numbers  
> 3. Always cite the referenced test (each snippet lists it).  
> 4. If something is missing, state it—do **not** invent APIs.

**Recommended system prompt snippet**
```
Before answering, read llm-docs/README.md. Only open other llm-docs files if the question requires them. 
Quote the relevant test case for every code example. 
If the docs lack the needed info, explicitly say so instead of guessing.
```

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

| File | Purpose | Highlights |
|------|---------|------------|
| **README.md** | Navigation + instructions | How to consume docs efficiently |
| **QUICKSTART.md** | 30-second guide | Install, core idea, dual-context example |
| **API.yaml** | Complete API reference | Signatures, behaviors, caching, tests |
| **PATTERNS.md** | Common scenarios | 9 tested patterns + anti-pattern |
| **EXAMPLES.md** | Working code | 10 runnable snippets straight from tests |
| **CHANGELOG.md** | Version history | Features, coverage, compatibility notes |

**Total**: ~1K dense lines vs. ~2.5K human-doc lines → **≈60% token reduction**

## Quick Navigation

### For Quick Understanding
Start with: **QUICKSTART.md** (30 seconds to understand SmartAsync)

### For API Reference
Go to: **API.yaml** (complete structured reference)

### For Common Use Cases
Read: **PATTERNS.md** (tested scenarios + anti-pattern)

### For Complete Examples
See: **EXAMPLES.md** (10 runnable snippets with test references)

### For Version Changes
Check: **CHANGELOG.md** (v0.1.0 feature list)

## Key Features (Quick Reference)

**What it does**: Bidirectional decorator for methods and standalone functions working in both sync and async contexts

**Core behavior**:
- Async method in sync context → `asyncio.run()`
- Sync method in async context → `asyncio.to_thread()`
- Async method in async context → native coroutine
- Sync method in sync context → pass-through

**Performance**: ~1-2μs (async cached), ~100μs (sync context), ~50-100μs (thread offload)

**Dependencies**: None (stdlib only)

**Python**: 3.10+ (uses pattern matching)

**Test coverage**: 100% (14 tests, `tests/test_smartasync.py`)

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

All examples are extracted from **tests/test_smartasync.py** (495 lines, 14 tests, 100% coverage).

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
