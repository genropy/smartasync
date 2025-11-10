# SmartAsync Scenarios

Questa directory contiene guide dettagliate per scenari d'uso specifici di SmartAsync, numerate in ordine logico di apprendimento.

## 📚 Scenari Disponibili

### Fondamentali (1-3)
Scenari base per iniziare con SmartAsync

1. **[01: CLI Tools with Async Libraries](01-cli-tools-async-libs.md)**
   - 🎯 **Problema**: CLI tool che deve usare librerie async moderne
   - 💡 **Soluzione**: Chiamare async senza `asyncio.run()` boilerplate
   - 📝 **Esempio**: GitHub CLI con httpx
   - 👥 **Target**: CLI developers, script writers

2. **[02: Async App → Sync Legacy Library](02-async-app-sync-legacy.md)**
   - 🎯 **Problema**: FastAPI/Django che usa database sync legacy
   - 💡 **Soluzione**: Auto-threading di codice sync in contesto async
   - 📝 **Esempio**: FastAPI + SQLite sync
   - 👥 **Target**: Web developers, backend engineers

3. **[03: Testing Async Code](03-testing-async-code.md)**
   - 🎯 **Problema**: Test async verbosi, richiedono pytest-asyncio
   - 💡 **Soluzione**: Test sync semplici che funzionano con codice async
   - 📝 **Esempio**: Test suite senza plugin
   - 👥 **Target**: QA engineers, developers

### Architettura (4-6)
Design patterns e architetture avanzate

4. **[04: Unified Library API](04-unified-library-api.md)**
   - 🎯 **Problema**: Mantenere due implementazioni (sync e async)
   - 💡 **Soluzione**: Single implementation per entrambi gli utenti
   - 📝 **Esempio**: HTTP client universale
   - 👥 **Target**: Library authors

5. **[05: Gradual Migration](05-gradual-migration.md)**
   - 🎯 **Problema**: Migrare legacy codebase sync a async
   - 💡 **Soluzione**: Migrazione incrementale senza breaking changes
   - 📝 **Esempio**: Refactoring progressivo a fasi
   - 👥 **Target**: Maintainer di progetti legacy

6. **[06: Plugin Systems](06-plugin-systems.md)**
   - 🎯 **Problema**: Plugin system che supporta plugin sync e async
   - 💡 **Soluzione**: Pipeline che accetta entrambi i tipi
   - 📝 **Esempio**: Data processing pipeline
   - 👥 **Target**: Framework developers

### Integrazione (7-9)
Scenari di integrazione framework e tool

7. **[07: Mixed Framework Integration](07-mixed-framework.md)**
   - 🎯 **Problema**: Integrare Flask (sync) con microservices async
   - 💡 **Soluzione**: Chiamare async da sync framework seamlessly
   - 📝 **Esempio**: Flask + async API clients
   - 👥 **Target**: System architects

8. **[08: Web Scraping](08-web-scraping.md)**
   - 🎯 **Problema**: Mix async I/O fetch + sync BeautifulSoup parsing
   - 💡 **Soluzione**: Parsing sync non blocca event loop
   - 📝 **Esempio**: Concurrent scraping con parsing offloaded
   - 👥 **Target**: Scraper developers

9. **[09: Interactive Environments](09-interactive-environments.md)**
   - 🎯 **Problema**: Jupyter notebooks e async/await verboso
   - 💡 **Soluzione**: Chiamare async senza await in REPL
   - 📝 **Esempio**: Data analysis in notebook
   - 👥 **Target**: Data scientists, researchers

## Come Usare Questi Documenti

Ogni documento include:
- 📋 **Problema**: Descrizione del caso d'uso
- 🔴 **Senza SmartAsync**: Approccio tradizionale (problemi)
- 🟢 **Con SmartAsync**: Soluzione migliorata
- 💡 **Esempio Completo**: Codice pronto all'uso
- ⚠️ **Considerazioni**: Limiti e best practices
- 🔗 **Risorse**: Link a esempi e riferimenti

## Quick Reference

| Hai bisogno di... | Vai a |
|-------------------|-------|
| CLI tool con httpx/aiohttp | [A1](a1-cli-tools-async-libs.md) |
| FastAPI + DB sync | [A2](a2-async-calls-sync-legacy.md) |
| Migrare codice legacy | [A3](a3-gradual-migration.md) |
| Library per entrambi gli utenti | [B1](b1-unified-library-api.md) |
| Sistema di plugin flessibile | [B2](b2-plugin-systems.md) |
| Test più semplici | [C1](c1-testing-async-code.md) |
| Notebook Jupyter | [C2](c2-interactive-environments.md) |
| Integrare Flask e async | [D1](d1-mixed-framework-integration.md) |
| Web scraper efficiente | [D2](web-scraping.md) |

## Prossimi Scenari

Scenari in programma:
- E1: Configuration Management
- E2: Message Queue Integration
- E3: Microservices Communication
- E4: File Processing Pipelines

---

**Feedback?** Apri un issue su GitHub con tag `documentation`.
