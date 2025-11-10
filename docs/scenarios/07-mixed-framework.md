# Scenario 07: Mixed Framework Integration

**Target Audience**: System architects, backend engineers
**Difficulty**: Advanced
**Keywords**: microservices, integration, flask, fastapi, mixed architecture

---

## 📋 The Problem

Modern systems often mix sync and async frameworks:

**Common scenarios**:
- Legacy Flask/Django app + new async microservices
- Sync web framework + async message queue
- Traditional app + async external APIs
- Gradual migration to async architecture

**Integration challenges**:
- Flask (sync) needs to call async API clients
- Celery (sync) tasks need async HTTP requests
- Django (mixed) views calling async services
- Sync middleware calling async backends

**Traditional solutions are painful**:
- Manual `asyncio.run()` everywhere
- Thread pool management
- Event loop lifecycle
- Complex error handling
- Boilerplate code duplication

---

## 💡 Solution with SmartAsync

**Seamless cross-framework calls**:

- Sync framework can call async clients naturally
- No manual event loop management
- Clean, maintainable code
- Each framework in its comfort zone
- Automatic adaptation at boundaries

**Pattern**:
```
Sync Framework (Flask, Django)
  └─→ Service Layer (@smartasync methods)
        ├─→ Async HTTP client (httpx)
        ├─→ Async message queue (aio-pika)
        ├─→ Async database (asyncpg)
        └─→ Async cache (aioredis)
```

Service layer adapts automatically to sync framework context.

---

## 🎯 When to Use

**Ideal for**:
- Microservices architectures
- Legacy system modernization
- Multi-framework applications
- Service mesh integration
- API gateway patterns
- BFF (Backend for Frontend) layers

**Perfect when**:
- Cannot rewrite entire application
- Need to use modern async libraries
- Want to isolate integration complexity
- Multiple frameworks in same codebase
- Gradual architectural evolution

---

## ⚠️ Considerations

### Architecture Patterns

**Service Layer Pattern**:
- Sync framework at edges
- Async operations in service layer
- SmartAsync bridges the gap
- Clean separation of concerns

**Adapter Pattern**:
- Create adapters with @smartasync
- Framework calls adapters
- Adapters handle async complexity
- Swap implementations easily

**Facade Pattern**:
- Single unified interface
- Hide async/sync complexity
- Framework-agnostic
- Testable in isolation

### Performance Implications

**Request latency**:
- Each async call: ~100μs overhead
- Usually negligible vs network I/O
- Batch operations if possible
- Monitor and optimize hot paths

**Concurrency model**:
- Sync frameworks: thread-per-request
- Async clients: event loop per request
- Thread-safe resource management
- Connection pooling strategy

**Resource usage**:
- Memory: Event loop per request
- Threads: OS thread pool
- Connections: Pool properly
- Monitor in production

### Testing Strategy

**Unit tests**:
- Test service layer in isolation
- Both sync and async contexts
- Mock external dependencies
- Fast execution

**Integration tests**:
- Real frameworks
- Real async clients
- Test full request cycle
- Slower but thorough

**Load tests**:
- Measure actual performance
- Compare vs pure sync/async
- Find bottlenecks
- Tune configuration

### When NOT to Use

**Avoid if**:
- Building new app from scratch (choose one framework)
- Performance critical (microsecond-level)
- Simple CRUD app (no need for complexity)
- All services are sync-only

**Better alternatives**:
- Rewrite to fully async (FastAPI, aiohttp)
- Stay fully sync if no I/O benefits
- Use dedicated service mesh
- Message queue for decoupling

---

## 🔗 Related Scenarios

- **02: Async App → Sync Legacy** - Opposite direction
- **05: Gradual Migration** - Systematic modernization
- **06: Plugin Systems** - Similar integration pattern

---

## 📚 Integration Examples

### Flask + Async Services
- Flask app (sync)
- httpx for API calls (async)
- aioredis for caching (async)
- SmartAsync service layer

### Django + Microservices
- Django views (mixed sync/async)
- Async service clients
- Async Celery tasks (modern)
- Unified interface

### Celery + Modern APIs
- Celery workers (sync)
- Async HTTP clients
- Async message queues
- Clean task definitions

---

## 🎯 Integration Success Criteria

Integration is successful when:
- Clean separation of framework and logic
- No asyncio.run() in business code
- Easy to test
- Good performance
- Simple error handling
- Clear architectural boundaries

---

## 🔍 Common Pitfalls

**Anti-patterns to avoid**:
- Leaking async into framework code
- Manual loop management in views
- Inconsistent error handling
- No connection pooling
- Ignoring performance monitoring

**Best practices**:
- Service layer abstraction
- Consistent error handling strategy
- Proper resource lifecycle
- Logging and monitoring
- Documentation of boundaries

---

## 📊 Decision Framework

**Choose full async when**:
- New project
- High concurrency needs
- Modern stack acceptable

**Choose SmartAsync integration when**:
- Legacy system
- Gradual migration
- Mixed requirements
- Risk-averse organization

**Stay full sync when**:
- Simple CRUD
- Low traffic
- No I/O benefits
- Team unfamiliar with async

---

**Next Steps**:
- See [02: Async App → Sync Legacy](02-async-app-sync-legacy.md) for reverse pattern
- Check [05: Gradual Migration](05-gradual-migration.md) for migration strategy
