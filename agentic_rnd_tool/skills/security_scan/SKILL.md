---
name: security_scan
description: "Use when: performing security assessments, vulnerability scanning, penetration testing, identifying security issues, running OWASP ZAP scans, or conducting security audits. This skill integrates with ZAP for comprehensive security testing."
triggers:
  - security
  - vulnerability
  - scan
  - penetration test
  - pentest
  - ZAP
  - OWASP
  - security audit
version: 1.0.0
author: "Agentic Framework"
---

# Security Scan Skill

## Purpose
Autonomously conduct security assessments and vulnerability scanning using OWASP ZAP and other security tools.

## ⚠️ Important Warnings

**Legal Disclaimer**: Only scan applications you own or have explicit permission to test. Unauthorized security testing is illegal.

**Impact**: Active scanning can:
- Generate significant traffic
- Trigger security alerts
- Modify application data
- Cause service disruptions

**Always get authorization before running active scans.**

## Capabilities

### Passive Scanning
- Traffic analysis
- Cookie security assessment
- Header analysis
- SSL/TLS configuration check
- Information disclosure detection

### Active Scanning
- SQL injection testing
- XSS vulnerability detection
- CSRF token validation
- Directory traversal testing
- Command injection checks
- Authentication bypass attempts

### Spider/Crawling
- Application mapping
- Endpoint discovery
- Form detection
- API discovery

### Reporting
- HTML report generation
- JSON export for automation
- XML reports
- CVE mapping
- Risk classification (Critical, High, Medium, Low)

## Usage

### Basic Security Scan
```python
from zap import SecurityScanner

scanner = SecurityScanner()
results = scanner.scan(
    target="https://testsite.example.com",
    scan_type="passive",
    report_format=["html", "json"]
)
```

### Full Security Assessment
```python
results = scanner.full_assessment(
    target="https://webapp.example.com",
    include_spider=True,
    include_active=True,  # Requires confirmation
    max_duration=3600
)
```

### API Security Testing
```python
results = scanner.scan_api(
    openapi_spec="https://api.example.com/swagger.json",
    auth_token="Bearer xxx",
    test_auth=True
)
```

## Configuration

### Input Parameters
- `target` (str): Target URL or IP address
- `scan_type` (str): "passive", "active", or "full"
- `scope` (list): URLs to include in scope
- `exclude` (list): URLs to exclude
- `auth` (dict): Authentication credentials
- `max_duration` (int): Maximum scan time in seconds
- `intensity` (str): "low", "medium", "high"

### Output Format
```json
{
  "target": "https://example.com",
  "scan_start": "2026-03-24T10:00:00Z",
  "scan_end": "2026-03-24T10:15:00Z",
  "scan_type": "passive",
  "alerts": [
    {
      "alert_id": "10021",
      "name": "X-Content-Type-Options Header Missing",
      "risk": "Low",
      "confidence": "Medium",
      "description": "The Anti-MIME-Sniffing header...",
      "solution": "Add X-Content-Type-Options: nosniff",
      "url": "https://example.com/page",
      "cwe_id": "16",
      "wasc_id": "15"
    }
  ],
  "summary": {
    "critical": 0,
    "high": 2,
    "medium": 5,
    "low": 12,
    "informational": 8
  },
  "report_paths": {
    "html": "./reports/scan_20260324_100000.html",
    "json": "./reports/scan_20260324_100000.json"
  }
}
```

## Scan Types

### 1. Passive Scan (Safe)
- No intrusive requests
- Analyzes existing traffic
- Safe for production
- Fast (minutes)

### 2. Spider Only
- Maps application structure
- Discovers endpoints
- Follows links
- Relatively safe

### 3. Active Scan (Intrusive)
- Tests for vulnerabilities
- Sends malicious payloads
- May trigger alerts
- Requires authorization
- Slow (hours)

## Security Best Practices

### Pre-Scan Checklist
- [ ] Written authorization obtained
- [ ] Scan scope defined
- [ ] Exclusion list configured
- [ ] Maintenance window scheduled (for active scans)
- [ ] Stakeholders notified
- [ ] Backup verification complete

### During Scan
- Monitor application health
- Watch for unexpected behavior
- Be ready to stop scan
- Log all activities

### Post-Scan
- Review findings
- Validate vulnerabilities
- Prioritize remediation
- Generate report
- Store in memory for tracking

## Integration with OWASP ZAP

### ZAP Setup
```bash
# Install ZAP
docker run -p 8080:8080 owasp/zap2docker-stable zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.key=changeme

# Or install locally
# https://www.zaproxy.org/download/
```

### API Configuration
See [TOOLS.md](../../TOOLS.md) for ZAP API configuration:
```yaml
zap:
  api_key: "changeme"
  host: "localhost"
  port: 8080
```

## Error Handling

### Common Issues
- **ZAP Not Running**: Check if ZAP daemon is active
- **Connection Refused**: Verify host/port in TOOLS.md
- **Timeout**: Increase scan timeout for large applications
- **Authentication Failed**: Verify credentials

### Failure Recovery
- Save partial results
- Log error details to MEMORY.md
- Retry with reduced scope
- Fall back to passive scan only

## Performance

### Optimization
- Limit scan scope
- Use parallel scanning for multiple targets
- Adjust thread count
- Set reasonable timeouts
- Use API mode (faster than GUI)

### Resource Limits
- Max memory: 2GB
- Max scan duration: 1 hour (configurable)
- Max concurrent scans: 1 (prevent resource exhaustion)

## Compliance & Standards

### Frameworks Supported
- OWASP Top 10
- CWE (Common Weakness Enumeration)
- WASC Threat Classification
- PCI DSS scanning requirements

### Reporting Standards
- CVE references
- CVSS scoring
- Remediation guidance
- Compliance mapping

## Integration

This skill integrates with:
- **TOOLS.md**: ZAP and security tool configuration
- **MEMORY.md**: Track scan history and vulnerability trends
- **workflows/**: Part of security audit workflows
- **web_research**: Can scan URLs found during research

## Examples

### Example 1: Quick Passive Scan
```python
results = scanner.scan(
    target="https://newapp.example.com",
    scan_type="passive",
    max_duration=300
)
```

### Example 2: Authenticated Scan
```python
results = scanner.scan(
    target="https://webapp.example.com",
    scan_type="full",
    auth={
        "type": "form",
        "login_url": "https://webapp.example.com/login",
        "username_field": "email",
        "password_field": "password",
        "username": "testuser",
        "password": "testpass"
    }
)
```

### Example 3: API Testing
```python
results = scanner.scan_api(
    openapi_spec="./api-spec.yaml",
    base_url="https://api.example.com",
    api_key="test_key_123"
)
```

## See Also
- [zap.py](zap.py) - Implementation
- [../web_research/SKILL.md](../web_research/SKILL.md) - Related skill
- [OWASP ZAP Documentation](https://www.zaproxy.org/docs/)