# Memory

## Session Context

### Active Session
```yaml
session_id: null
start_time: null
current_workflow: null
active_agents: []
```

## Knowledge Base

### Research History
```yaml
topics_researched: []
urls_visited: []
key_findings: []
failed_sources: []
```

### Security Scans
```yaml
targets_scanned: []
vulnerabilities_found: []
scan_reports: []
last_scan_date: null
```

## Inter-Agent Communication

### Message Queue
When agents need to share data:
```yaml
messages:
  - from: web_research
    to: orchestrator
    timestamp: "2026-03-24T10:30:00Z"
    data:
      urls_found: 45
      content_extracted: true
```

### Shared Context
```yaml
shared_data:
  current_target: null
  research_topic: null
  scan_scope: []
  findings_summary: {}
```

## Persistent Storage

### Long-term Memory
Store important insights across sessions:
```yaml
learned_patterns:
  - pattern: "financial sites often require JavaScript rendering"
    agent: web_research
    confidence: 0.9
  
  - pattern: "WordPress sites commonly have /wp-admin endpoint"
    agent: security_scan
    confidence: 0.95

successful_strategies:
  - task: "competitive analysis"
    approach: "parallel scraping + sentiment analysis"
    success_rate: 0.87
```

### Failure Log
Learn from mistakes:
```yaml
failed_attempts:
  - task: "scrape site X"
    reason: "cloudflare protection"
    attempted_solutions: ["selenium", "requests"]
    resolution: "use_proxy"
```

## Memory Operations

### Save to Memory
```python
def save_to_memory(key, value, scope="session"):
    """
    Save data to memory
    scope: "session" (temporary) or "persistent" (long-term)
    """
    pass
```

### Retrieve from Memory
```python
def get_from_memory(key, scope="session"):
    """
    Retrieve data from memory
    Returns None if key doesn't exist
    """
    pass
```

### Clear Memory
```python
def clear_memory(scope="session"):
    """
    Clear memory for given scope
    Use with caution - persistent clears are permanent
    """
    pass
```

## Current Session Data

<!-- Sub-agents will append their results here -->

---

**Last Updated**: Never  
**Total Sessions**: 0  
**Total Research Tasks**: 0  
**Total Security Scans**: 0