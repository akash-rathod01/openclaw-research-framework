# Tool Configuration

## Browser Tools

### Selenium WebDriver
```yaml
browser:
  enable: true
  driver: chrome
  headless: true
  options:
    - "--no-sandbox"
    - "--disable-dev-shm-usage"
    - "--disable-gpu"
  timeout: 30
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

### Playwright (Alternative)
```yaml
playwright:
  enable: false
  browser: chromium
  headless: true
```

## HTTP Client

### Requests Library
```yaml
http_client:
  enable: true
  timeout: 30
  max_retries: 3
  headers:
    User-Agent: "ResearchBot/1.0"
  proxy:
    enable: false
    http: null
    https: null
```

## Security Tools

### OWASP ZAP
```yaml
zap:
  enable: true
  api_key: "changeme"
  host: "localhost"
  port: 8080
  scan_types:
    - spider
    - active_scan
    - passive_scan
  report_format: ["html", "json", "xml"]
```

### Nmap (Optional)
```yaml
nmap:
  enable: false
  scan_args: "-sV -sC"
```

## Scraping Tools

### BeautifulSoup
```yaml
beautifulsoup:
  enable: true
  parser: "html.parser"  # or "lxml", "html5lib"
```

### Scrapy
```yaml
scrapy:
  enable: false
  concurrent_requests: 16
  download_delay: 0
  robotstxt_obey: true
```

## Data Processing

### Pandas
```yaml
pandas:
  enable: true
  max_rows_display: 100
```

### JSON/YAML Parsers
```yaml
parsers:
  json: true
  yaml: true
  xml: true
  csv: true
```

## AI/NLP Tools

### Text Analysis
```yaml
nlp:
  enable: false
  provider: "openai"  # or "local", "huggingface"
  model: "gpt-4"
```

## Storage

### Local File System
```yaml
storage:
  enable: true
  base_path: "./data"
  subdirs:
    - research
    - scans
    - reports
    - temp
```

### Database (Optional)
```yaml
database:
  enable: false
  type: "sqlite"  # or "postgresql", "mongodb"
  path: "./data/agent.db"
```

## Logging

```yaml
logging:
  enable: true
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "./logs/agent.log"
  rotation: "daily"
  max_size: "10MB"
```

## API Integrations

### Search APIs
```yaml
search_apis:
  google:
    enable: false
    api_key: null
  bing:
    enable: false
    api_key: null
```

### Social Media
```yaml
social:
  twitter:
    enable: false
    api_key: null
  reddit:
    enable: false
    client_id: null
```

## Rate Limiting

```yaml
rate_limiting:
  enable: true
  requests_per_second: 10
  burst_size: 20
```