---
name: web_research
description: "Use when: researching topics online, scraping websites, gathering information from multiple sources, extracting web content, following links, or conducting competitive analysis. This skill performs deep web research using BeautifulSoup and Selenium."
triggers:
  - research
  - scrape
  - web search
  - gather data
  - find information
  - competitive analysis
version: 1.0.0
author: "Agentic Framework"
---

# Web Research Skill

## Purpose
Autonomously research topics by scraping websites, extracting content, and aggregating information from multiple sources.

## Capabilities

### Content Extraction
- HTML parsing with BeautifulSoup
- JavaScript rendering with Selenium
- PDF text extraction
- Image metadata extraction
- Structured data parsing (JSON-LD, microdata)

### Multi-Source Aggregation
- Parallel scraping of multiple URLs
- Link following with depth limits
- Deduplication of content
- Source credibility assessment

### Data Processing
- Text cleaning and normalization
- Entity extraction
- Keyword identification
- Summary generation

## Usage

### Basic Research
```python
from scraper import WebResearcher

researcher = WebResearcher()
results = researcher.research(
    topic="AI frameworks 2026",
    max_sources=20,
    depth=2
)
```

### Targeted Scraping
```python
results = researcher.scrape_urls([
    "https://example.com/page1",
    "https://example.com/page2"
], extract_links=True)
```

### JavaScript-Heavy Sites
```python
results = researcher.scrape_dynamic(
    url="https://spa-site.com",
    wait_for_element="#content",
    scroll=True
)
```

## Configuration

### Input Parameters
- `topic` (str): Research topic or query
- `max_sources` (int): Maximum number of sources to scrape
- `depth` (int): How many link levels to follow (1-5)
- `language` (str): Preferred content language
- `date_range` (tuple): Filter by publication date
- `domains` (list): Restrict to specific domains

### Output Format
```json
{
  "topic": "research query",
  "sources_found": 45,
  "sources_scraped": 42,
  "content": [
    {
      "url": "https://...",
      "title": "Article Title",
      "content": "Extracted text...",
      "metadata": {},
      "timestamp": "2026-03-24T10:30:00Z"
    }
  ],
  "summary": "Key findings...",
  "failed_urls": []
}
```

## Error Handling

### Common Issues
- **Cloudflare Protection**: Automatically retry with Selenium
- **Rate Limiting**: Implement exponential backoff
- **404/403 Errors**: Skip and log in failed_urls
- **Timeout**: Cancel after 30s per page

### Failure Recovery
- Store partial results on error
- Continue with remaining URLs
- Report issues in memory for learning

## Performance

### Optimization Strategies
- Use connection pooling
- Cache responses
- Parallel requests (max 10 concurrent)
- Respect robots.txt
- Implement polite crawling delays

### Resource Limits
- Max memory: 512MB
- Max execution time: 5 minutes
- Max content size per page: 10MB

## Integration

This skill integrates with:
- **TOOLS.md**: Browser and HTTP client configuration
- **MEMORY.md**: Store research history and patterns
- **workflows/research.md**: Part of larger research workflow

## Examples

### Example 1: Competitive Analysis
```python
results = researcher.research(
    topic="competitor products",
    domains=["competitor1.com", "competitor2.com"],
    extract_pricing=True
)
```

### Example 2: News Aggregation
```python
results = researcher.research(
    topic="AI breakthroughs",
    date_range=("2026-03-01", "2026-03-24"),
    max_sources=50,
    language="en"
)
```

## See Also
- [scraper.py](scraper.py) - Implementation
- [index.ts](index.ts) - TypeScript interface
- [../security_scan/SKILL.md](../security_scan/SKILL.md) - Related skill