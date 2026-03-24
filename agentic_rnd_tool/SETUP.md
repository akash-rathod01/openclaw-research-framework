# Setup Guide - Agentic RnD Tool

Complete setup instructions for the multi-agent research and security framework.

## 📋 System Requirements

- **Python**: 3.9 or higher
- **Node.js**: 18.0 or higher (for TypeScript interface)
- **Docker**: Optional, for OWASP ZAP
- **OS**: Windows, macOS, or Linux

## 🔧 Installation

### Step 1: Clone/Download Repository

```bash
cd path/to/agentic_rnd_tool
```

### Step 2: Python Setup

#### Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Install ChromeDriver (for Selenium)

**Option A: Automatic (recommended)**
```bash
# Installed automatically with webdriver-manager
# No manual setup needed
```

**Option B: Manual**
- Download from: https://chromedriver.chromium.org/
- Add to system PATH

### Step 3: Node.js Setup (Optional)

Only needed if using TypeScript interface:

```bash
# Install Node.js dependencies
npm install

# Build TypeScript
npm run build
```

### Step 4: OWASP ZAP Setup (for Security Scanning)

#### Option A: Docker (Recommended)

```bash
# Pull and run ZAP in daemon mode
docker run -d -p 8080:8080 --name zap \
  owasp/zap2docker-stable zap.sh -daemon \
  -host 0.0.0.0 -port 8080 -config api.key=changeme

# Verify ZAP is running
curl http://localhost:8080/JSON/core/view/version/
```

#### Option B: Local Installation

1. Download from: https://www.zaproxy.org/download/
2. Install ZAP
3. Run in daemon mode:
   ```bash
   zap.sh -daemon -host localhost -port 8080 -config api.key=changeme
   ```

### Step 5: Configuration

#### Update TOOLS.md

Edit ZAP configuration if needed:
```yaml
zap:
  enable: true
  api_key: "changeme"  # Match your ZAP config
  host: "localhost"
  port: 8080
```

#### Update USER.md

Set your preferences:
```yaml
research:
  max_sources: 50
  depth_level: 2
  output_format: "markdown"

security:
  scan_intensity: "medium"
  include_active: false  # Set true only for authorized testing
```

## ✅ Verify Installation

### Test Web Research Agent

```bash
cd skills/web_research
python scraper.py "test search query"
```

Expected output:
```
🔍 Starting research on: test search query
📊 Max sources: 50, Depth: 2
✅ Research complete: N sources
💾 Results saved to: research_results_YYYYMMDD_HHMMSS.json
```

### Test Security Scanner

```bash
cd skills/security_scan
python zap.py https://example.com passive
```

Expected output:
```
✅ Connected to OWASP ZAP
🔒 Starting passive security scan on: https://example.com
...
✅ Scan complete: N alerts found
```

### Test TypeScript Interface (if installed)

```bash
npm test
```

## 🚀 Running the Framework

### Basic Research

```python
from skills.web_research.scraper import WebResearcher

researcher = WebResearcher()
results = researcher.research(
    topic="AI frameworks 2026",
    max_sources=20,
    depth=2
)

# Save results
researcher.save_results(results, "my_research.json")
```

### Security Scanning

```python
from skills.security_scan.zap import SecurityScanner

scanner = SecurityScanner()

# Passive scan (safe)
results = scanner.scan(
    target="https://testsite.example.com",
    scan_type="passive",
    report_format=["html", "json"]
)

print(f"Found {len(results['alerts'])} security issues")
print(f"Report: {results['report_paths']['html']}")
```

### Using Workflows

```python
# Import orchestrator (to be implemented)
from orchestrator import Orchestrator

orch = Orchestrator()
results = orch.run_workflow(
    workflow="research",
    topic="competitive analysis",
    include_security=True
)
```

## 🔍 Troubleshooting

### Python Issues

**Problem**: `ModuleNotFoundError: No module named 'requests'`
```bash
# Solution: Activate venv and reinstall
pip install -r requirements.txt
```

**Problem**: Selenium can't find ChromeDriver
```bash
# Solution: Install webdriver-manager
pip install webdriver-manager
```

### ZAP Issues

**Problem**: "Could not connect to ZAP"
```bash
# Check if ZAP is running
curl http://localhost:8080/JSON/core/view/version/

# Start ZAP if not running
docker start zap
# Or manually: zap.sh -daemon -host localhost -port 8080
```

**Problem**: ZAP API key mismatch
```bash
# Update TOOLS.md with correct API key
# Default is "changeme"
```

### Node.js Issues

**Problem**: TypeScript compilation errors
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 🔐 Security Best Practices

### For Web Research
1. ✅ Respect robots.txt
2. ✅ Use reasonable delays between requests
3. ✅ Identify your bot with proper User-Agent
4. ✅ Don't overwhelm servers with parallel requests
5. ⚠️ Be aware of legal implications of scraping

### For Security Scanning
1. ⚠️ **ONLY** scan applications you own or have permission to test
2. ⚠️ Get written authorization before active scanning
3. ⚠️ Notify stakeholders before scanning
4. ⚠️ Use passive scans on production systems
5. ⚠️ Schedule active scans during maintenance windows
6. ✅ Log all scanning activities
7. ✅ Store scan results securely

## 📝 Configuration Guide

### Environment Variables

Create `.env` file:
```bash
# API Keys
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# ZAP Configuration
ZAP_API_KEY=changeme
ZAP_HOST=localhost
ZAP_PORT=8080

# Research Settings
MAX_SOURCES=50
RESEARCH_DEPTH=2

# Logging
LOG_LEVEL=INFO
```

### Custom Configuration

Create `config.yaml`:
```yaml
research:
  default_sources: 50
  default_depth: 2
  timeout: 300
  
security:
  default_scan_type: passive
  timeout: 3600
  
logging:
  level: INFO
  file: ./logs/agent.log
```

## 📚 Next Steps

1. **Read Documentation**
   - [README.md](README.md) - Framework overview
   - [SOUL.md](SOUL.md) - Agent identity
   - [AGENTS.md](AGENTS.md) - Orchestration guide
   - [workflows/research.md](workflows/research.md) - Workflow details

2. **Explore Skills**
   - [skills/web_research/SKILL.md](skills/web_research/SKILL.md)
   - [skills/security_scan/SKILL.md](skills/security_scan/SKILL.md)

3. **Try Examples**
   - Simple web research
   - Passive security scan
   - Combined research + security workflow

4. **Customize**
   - Update USER.md with preferences
   - Create custom workflows
   - Add new sub-agents

## 🆘 Getting Help

- **Documentation**: Check all .md files in the project
- **Issues**: Check error messages carefully
- **Logs**: Review logs in `./logs/` directory
- **Community**: Open an issue on GitHub

## 🎓 Learning Resources

### Web Scraping
- BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/
- Selenium: https://www.selenium.dev/documentation/

### Security Testing
- OWASP ZAP: https://www.zaproxy.org/docs/
- OWASP Top 10: https://owasp.org/www-project-top-ten/

### Multi-Agent Systems
- OpenClaw: (documentation link)
- Agent orchestration patterns

## ✨ Success Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Python dependencies installed (`requirements.txt`)
- [ ] ChromeDriver available for Selenium
- [ ] OWASP ZAP running (if using security features)
- [ ] Node.js installed (if using TypeScript)
- [ ] Configuration files updated (TOOLS.md, USER.md)
- [ ] Test scripts run successfully
- [ ] `.env` file created (if using API keys)
- [ ] Logs directory exists

---

**Installation Complete!** 🎉

You're ready to use the Agentic RnD Tool for autonomous research and security assessment.

Start with simple examples and gradually explore more complex workflows.
