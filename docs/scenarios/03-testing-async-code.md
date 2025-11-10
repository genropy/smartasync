# Scenario 03: Testing Async Code

**Target Audience**: QA engineers, developers, test writers
**Difficulty**: Beginner
**Keywords**: pytest, unittest, testing, async tests, test automation

---

## 📋 The Problem

Testing async code traditionally requires:
- Special test frameworks (pytest-asyncio)
- Event loop setup boilerplate
- Different test patterns for sync vs async code
- Verbose test fixtures
- Complex setup/teardown for async resources

This creates friction:
- Simple code requires complex tests
- Test files become verbose
- New developers struggle with async test patterns
- Hard to mix sync and async test utilities

---

## 💡 Solution with SmartAsync

Write **simple synchronous tests** that work seamlessly with async code:

- No `pytest-asyncio` plugin needed
- No event loop management
- Test async methods like sync methods
- Same test patterns for all code
- Clean, readable test files

**Key Benefit**: Lower barrier to entry - anyone who can write basic tests can test async code.

---

## 🎯 When to Use

**Ideal for**:
- Unit tests for async APIs
- Testing async utilities and libraries
- CI/CD pipelines (simpler setup)
- Teams new to async Python
- Mixed sync/async codebases

**Also enables**:
- Quick REPL testing during development
- Simple test fixtures
- Standard unittest.TestCase support
- Gradual migration of test suites

---

## ⚠️ Considerations

### Performance
- Each test that calls async code spawns an event loop
- Still fast enough for most test suites
- Use native async tests if you need thousands of concurrent operations

### Coverage
- Works great for unit tests
- Integration tests may need real async context
- Mock async dependencies normally

### Alternatives
- **pytest-asyncio**: Better for tests that need persistent event loop
- **Native async tests**: Better for testing event loop behavior itself

---

## 🔗 Related Scenarios

- **01: CLI Tools** - Similar pattern (sync interface to async functionality)
- **04: Unified Library API** - Testing libraries that support both modes
- **09: Interactive Environments** - Similar REPL-friendly pattern

---

## 📚 References

- **pytest**: https://docs.pytest.org/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **unittest**: https://docs.python.org/3/library/unittest.html

---

**Next Steps**:
- See [01: Sync App → Async Libraries](01-sync-app-async-libs.md) for similar patterns
- Check [04: Unified Library API](04-unified-library-api.md) for library testing
