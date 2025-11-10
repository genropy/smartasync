# How SmartAsync Works - Technical Deep Dives

This directory contains in-depth technical explanations of SmartAsync's internals, suitable for developers who want to understand how the library works under the hood.

## Available Guides

### [Calling Async Code from Sync Context](calling-async-from-sync.md)

**Level**: Intermediate
**Topics Covered**:
- Python async/await fundamentals
- Coroutines and event loops explained
- Step-by-step breakdown of the `@smartasync` decorator
- Execution flow diagrams for all scenarios
- Caching strategy and design decisions
- Performance analysis and benchmarks
- Edge cases and error handling

**Best for**: Developers who want to understand the core mechanism behind SmartAsync.

---

## Coming Soon

### Context Detection Strategies (Planned)

Deep dive into how SmartAsync detects execution context:
- `asyncio.get_running_loop()` internals
- Alternative detection methods
- Thread-local state management
- Multi-process considerations

### Thread Safety Analysis (Planned)

Comprehensive analysis of thread safety:
- Why the cache is not thread-safe
- Race condition scenarios
- Mitigation strategies
- Performance impact of thread-safe alternatives

### Performance Optimization (Planned)

Detailed performance analysis:
- Benchmarking methodology
- Comparison with alternatives
- Optimization opportunities
- When performance matters vs when it doesn't

---

## Audience

These guides are written for:

- **✅ Backend developers** learning async patterns
- **✅ Library authors** considering SmartAsync for their projects
- **✅ Contributors** wanting to improve SmartAsync
- **✅ Advanced users** debugging edge cases

**Prerequisites**:
- Basic Python knowledge
- Familiarity with async/await syntax
- Understanding of decorators

---

## Related Documentation

### For Users
- [README](../../README.md) - Quick start and basic usage
- [Scenarios](../scenarios/) - Real-world use case guides
- [TECH-REPORT](../../TECH-REPORT.md) - Technical overview

### For Contributors
- [CONTRIBUTING](../../CONTRIBUTING.md) - How to contribute
- [GitHub Issues](https://github.com/genropy/smartasync/issues) - Bug reports and features

---

## Feedback

Found an error or have suggestions? Please:
1. Open an issue on [GitHub](https://github.com/genropy/smartasync/issues)
2. Tag it with `documentation`
3. Reference the specific document

---

**Last Updated**: 2025-11-10
