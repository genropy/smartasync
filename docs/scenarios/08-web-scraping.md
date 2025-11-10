# Scenario 08: Web Scraping

**Target Audience**: Scraper developers, data engineers
**Difficulty**: Intermediate
**Keywords**: web scraping, beautifulsoup, lxml, aiohttp, httpx, concurrent fetching

---

## 📋 The Problem

Web scraping has two distinct phases with different needs:

**Phase 1: Fetching (I/O bound)**
- Download HTML from many URLs
- Network-bound operation
- Perfect for async/await
- Want high concurrency

**Phase 2: Parsing (CPU bound)**
- Parse HTML with BeautifulSoup/lxml
- CPU-intensive operation
- Synchronous libraries
- Blocks event loop if not careful

**Traditional approaches**:

**All Sync**:
- Simple to write
- Sequential fetching (slow)
- Can't exploit concurrency
- Wastes time waiting

**Manual Async**:
- Async fetch with aiohttp
- Manual threading for parsing
- Complex coordination
- Error handling tricky
- Boilerplate heavy

**The dilemma**: Need async for fetching, sync for parsing.

---

## 💡 Solution with SmartAsync

**Natural separation of concerns**:

- Async fetch methods (network I/O)
- Sync parsing methods (CPU work)
- SmartAsync handles coordination
- Clean, maintainable code
- Automatic thread offloading

**Pattern**:
```
Scraper
  ├─→ fetch_url() - async (concurrent)
  ├─→ fetch_many() - async (concurrent)
  ├─→ parse_html() - sync (CPU-bound)
  └─→ extract_data() - sync (BeautifulSoup)
```

Framework coordinates async fetching + sync parsing automatically.

---

## 🎯 When to Use

**Ideal for**:
- Multi-page scraping
- Concurrent URL fetching
- BeautifulSoup/lxml parsing
- Data extraction pipelines
- Content aggregation
- Price monitoring
- Social media scraping

**Perfect when**:
- Need to fetch 100+ pages
- Parsing is CPU-intensive
- Want clean code separation
- Using sync parsing libraries
- Building scraping framework

---

## ⚠️ Considerations

### Design Patterns

**Concurrent fetching**:
- Use asyncio.gather() for multiple URLs
- Respect rate limits
- Handle retries gracefully
- Connection pooling

**Parsing strategy**:
- Parse in threads (don't block loop)
- Consider batch parsing
- Reuse BeautifulSoup parsers
- Cache parsed results

**Error handling**:
- Network errors (timeouts, 404s)
- Parse errors (malformed HTML)
- Rate limiting (429 responses)
- Graceful degradation

### Performance Optimization

**Fetching**:
- Connection pooling (httpx.AsyncClient)
- Concurrent requests limit
- Adaptive rate limiting
- DNS caching

**Parsing**:
- Choose right parser (lxml vs html.parser)
- Parse only what you need
- Stream large documents
- Consider parallel parsing

**Memory management**:
- Don't keep all HTML in memory
- Process and discard
- Use generators
- Monitor memory usage

### Ethical Considerations

**Best practices**:
- Respect robots.txt
- Implement rate limiting
- Use reasonable concurrency
- Set User-Agent header
- Cache responses
- Don't hammer servers

**Legal considerations**:
- Check terms of service
- Respect copyright
- Follow data protection laws
- Rate limiting requirements

### When NOT to Use

**Avoid if**:
- Scraping single page (no concurrency benefit)
- Site has official API (use that instead)
- JavaScript-heavy site (need browser automation)
- Real-time scraping (need websockets)

**Better alternatives**:
- **Scrapy** - Full-featured framework
- **Playwright/Selenium** - Browser automation
- **Official APIs** - Always prefer if available

---

## 🔗 Related Scenarios

- **01: CLI Tools** - Scraper as CLI tool
- **08: Interactive Environments** - Prototyping scrapers in Jupyter
- **06: Plugin Systems** - Scraping pipelines with plugins

---

## 📚 Technology Stack

**Fetching libraries**:
- **httpx** - Modern async HTTP client
- **aiohttp** - Popular async HTTP
- **requests** - Traditional sync (not ideal)

**Parsing libraries**:
- **BeautifulSoup** - Easy, flexible
- **lxml** - Fast, powerful
- **html5lib** - Strict HTML5 parsing
- **selectolax** - Very fast parser

**Frameworks**:
- **Scrapy** - Full scraping framework
- **newspaper3k** - Article extraction
- **trafilatura** - Content extraction

---

## 🎯 Scraper Architecture

**Layered design**:
```
1. Transport Layer (async)
   - HTTP client
   - Connection pooling
   - Rate limiting

2. Fetching Layer (async)
   - URL management
   - Retry logic
   - Error handling

3. Parsing Layer (sync + threading)
   - HTML parsing
   - Data extraction
   - Validation

4. Storage Layer (async or sync)
   - Database writes
   - File storage
   - Caching
```

SmartAsync bridges layers 2-3 automatically.

---

## 🔍 Common Challenges

**Rate limiting**:
- Implement delays between requests
- Respect Retry-After headers
- Exponential backoff
- Per-domain rate limits

**Session management**:
- Login flows
- Cookie handling
- CSRF tokens
- Session persistence

**Anti-scraping measures**:
- CAPTCHA detection
- IP blocking
- JavaScript challenges
- User-Agent checking

**Solutions**:
- Rotate User-Agents
- Use proxy rotation
- Implement delays
- Handle CAPTCHAs appropriately

---

## 📊 Performance Expectations

**Sync scraping**:
- 1 page/second (sequential)
- Limited by network latency
- Simple code

**Async scraping** (with SmartAsync):
- 10-50 pages/second (concurrent)
- Limited by bandwidth and rate limits
- Clean code
- Automatic thread offloading for parsing

**Scrapy** (comparison):
- 50-100+ pages/second
- More complex setup
- Full framework

---

## 🎯 Success Metrics

Your scraper is successful when:
- High concurrency without complexity
- Clean separation of fetch/parse
- Respects site resources
- Robust error handling
- Good performance
- Easy to maintain

---

**Next Steps**:
- See [01: CLI Tools](01-cli-tools-async-libs.md) for CLI scraper tools
- Check [09: Interactive Environments](09-interactive-environments.md) for prototyping
