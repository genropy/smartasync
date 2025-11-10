# SmartAsync Scenarios

This directory contains detailed guides for specific SmartAsync use cases, numbered in logical learning order.

## 📚 Available Scenarios

### Fundamentals (1-3)
Basic scenarios to get started with SmartAsync

1. **[01: Sync App → Async Libraries](01-sync-app-async-libs.md)**
   - 🎯 **Problem**: CLI tool needs to use modern async libraries
   - 💡 **Solution**: Call async without `asyncio.run()` boilerplate
   - 📝 **Example**: GitHub CLI with httpx
   - 👥 **Target**: CLI developers, script writers

2. **[02: Async App → Sync Legacy Library](02-async-app-sync-libs.md)**
   - 🎯 **Problem**: FastAPI/Django using legacy sync database
   - 💡 **Solution**: Auto-threading of sync code in async context
   - 📝 **Example**: FastAPI + SQLite sync
   - 👥 **Target**: Web developers, backend engineers

3. **[03: Testing Async Code](03-testing-async-code.md)**
   - 🎯 **Problem**: Verbose async tests, require pytest-asyncio
   - 💡 **Solution**: Simple sync tests that work with async code
   - 📝 **Example**: Test suite without plugins
   - 👥 **Target**: QA engineers, developers

### Architecture (4-6)
Design patterns and advanced architectures

4. **[04: Unified Library API](04-unified-library-api.md)**
   - 🎯 **Problem**: Maintaining two implementations (sync and async)
   - 💡 **Solution**: Single implementation for both user types
   - 📝 **Example**: Universal HTTP client
   - 👥 **Target**: Library authors

5. **[05: Gradual Migration](05-gradual-migration.md)**
   - 🎯 **Problem**: Migrating legacy sync codebase to async
   - 💡 **Solution**: Incremental migration without breaking changes
   - 📝 **Example**: Progressive phased refactoring
   - 👥 **Target**: Legacy project maintainers

6. **[06: Plugin Systems](06-plugin-systems.md)**
   - 🎯 **Problem**: Plugin system supporting both sync and async plugins
   - 💡 **Solution**: Pipeline accepting both types
   - 📝 **Example**: Data processing pipeline
   - 👥 **Target**: Framework developers

### Integration (7-9)
Framework and tool integration scenarios

7. **[07: Mixed Framework Integration](07-mixed-framework.md)**
   - 🎯 **Problem**: Integrating Flask (sync) with async microservices
   - 💡 **Solution**: Call async from sync framework seamlessly
   - 📝 **Example**: Flask + async API clients
   - 👥 **Target**: System architects

8. **[08: Web Scraping](08-web-scraping.md)**
   - 🎯 **Problem**: Mix async I/O fetch + sync BeautifulSoup parsing
   - 💡 **Solution**: Sync parsing doesn't block event loop
   - 📝 **Example**: Concurrent scraping with offloaded parsing
   - 👥 **Target**: Scraper developers

9. **[09: Interactive Environments](09-interactive-environments.md)**
   - 🎯 **Problem**: Jupyter notebooks and verbose async/await
   - 💡 **Solution**: Call async without await in REPL
   - 📝 **Example**: Data analysis in notebook
   - 👥 **Target**: Data scientists, researchers

## How to Use These Documents

Each document includes:
- 📋 **Problem**: Use case description
- 🔴 **Without SmartAsync**: Traditional approach (problems)
- 🟢 **With SmartAsync**: Improved solution
- 💡 **Complete Example**: Ready-to-use code
- ⚠️ **Considerations**: Limitations and best practices
- 🔗 **Resources**: Links to examples and references

## Quick Reference

| You need to... | Go to |
|----------------|-------|
| CLI tool with httpx/aiohttp | [01](01-sync-app-async-libs.md) |
| FastAPI + sync DB | [02](02-async-app-sync-libs.md) |
| Migrate legacy code | [05](05-gradual-migration.md) |
| Library for both users | [04](04-unified-library-api.md) |
| Flexible plugin system | [06](06-plugin-systems.md) |
| Simpler tests | [03](03-testing-async-code.md) |
| Jupyter notebook | [09](09-interactive-environments.md) |
| Integrate Flask and async | [07](07-mixed-framework.md) |
| Efficient web scraper | [08](08-web-scraping.md) |

## Upcoming Scenarios

Planned scenarios:
- Configuration Management
- Message Queue Integration
- Microservices Communication
- File Processing Pipelines

---

**Feedback?** Open an issue on GitHub with tag `documentation`.
