---
name: "Research & Security Orchestrator"
version: "1.0.0"
description: "Multi-agent orchestration system for research and security tasks"
---

# Agent Orchestration Configuration

## Lifecycle Hooks

### On Startup
```yaml
run:
  - load_memory          # Load persistent memory from previous sessions
  - initialize_tools     # Initialize browser, scrapers, security tools
  - check_subagents      # Verify all sub-agents are available
```

## Sub-Agent Registry

### Web Research Agent
```yaml
agent_id: web_research
skill_path: skills/web_research
triggers:
  - "research"
  - "scrape"
  - "web search"
  - "find information"
  - "gather data"
capabilities:
  - Web scraping (BeautifulSoup, Selenium)
  - Content extraction
  - Multi-source aggregation
  - Link following
tools_required:
  - browser
  - http_client
```

### Security Scan Agent
```yaml
agent_id: security_scan
skill_path: skills/security_scan
triggers:
  - "security"
  - "vulnerability"
  - "scan"
  - "penetration test"
  - "ZAP"
capabilities:
  - OWASP ZAP integration
  - Vulnerability scanning
  - Security report generation
  - CVE identification
tools_required:
  - zap_proxy
  - security_scanner
```

## Orchestration Strategies

### Sequential Execution
Use when sub-agent outputs feed into each other:
```yaml
strategy: sequential
flow:
  1. web_research -> extract URLs
  2. security_scan -> scan URLs
  3. synthesize -> generate report
```

### Parallel Execution
Use when sub-agents work independently:
```yaml
strategy: parallel
flow:
  - web_research: research_topic_A
  - web_research: research_topic_B
  - security_scan: scan_target_C
  wait: all_complete
  then: synthesize_results
```

### Conditional Execution
Use when decisions depend on results:
```yaml
strategy: conditional
flow:
  1. web_research -> gather_data
  2. if data.contains("webapp"):
       spawn: security_scan
     else:
       spawn: web_research (deep_dive)
```

## Memory Management

### Context Sharing
```yaml
memory:
  scope: shared           # All sub-agents access same memory
  persistence: file       # Save to MEMORY.md
  sync: real-time         # Updates visible immediately
```

### Result Aggregation
```yaml
aggregation:
  mode: hierarchical
  parent: orchestrator
  children: [web_research, security_scan]
  merge_strategy: append_with_metadata
```

## Error Handling

```yaml
error_handling:
  retry_failed_agents: 3
  timeout_per_agent: 300s
  fallback: partial_results
  log_level: info
```

## Workflow Integration

Load workflows from `workflows/` directory:
```yaml
workflows:
  - research.md          # Multi-stage research workflow
  - security_audit.md    # Full security assessment workflow
```