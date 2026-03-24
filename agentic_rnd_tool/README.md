# Agentic RnD Tool

**Multi-Agent Research & Security Framework powered by OpenClaw**

An autonomous multi-agent system for conducting web research and security assessments through intelligent orchestration of specialized sub-agents.

## 🌟 Overview

This framework provides a complete multi-agent orchestration system where:
- **One main orchestrator** coordinates specialized sub-agents
- **Sub-agents** handle specific domains (web research, security scanning)
- **Shared memory** enables learning and context sharing across agents
- **Workflows** define complex multi-stage processes
- **Tools** integrate with external systems (browsers, security scanners)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         Main Orchestrator Agent (SOUL.md)       │
│   Identity, Personality, Orchestration Logic    │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │   AGENTS.md     │  ← Coordination & Execution
        │   MEM  ORY.md     │  ← Shared Memory
        │   TOOLS.md      │  ← Tool Configuration
        │   USER.md       │  ← User Preferences
        └────────┬────────┘
                 │
     ┌───────────┴───────────┐
     │                       │
┌────▼─────┐          ┌─────▼─────┐
│  Web     │          │ Security  │
│ Research │          │   Scan    │
│ Sub-Agent│          │ Sub-Agent │
└──────────┘          └───────────┘
     │                      │
┌────▼─────┐          ┌─────▼─────┐
│scraper.py│          │  zap.py   │
│index.ts  │          │           │
└──────────┘          └───────────┘
```

## 📁 Project Structure

```
agentic_rnd_tool/
├── SOUL.md                    # Agent identity & personality
├── AGENTS.md                  # Orchestration configuration
├── MEMORY.md                  # Shared memory system
├── TOOLS.md                   # Tool configurations
├── USER.md                    # User preferences
├── openclaw.json              # OpenClaw framework config
│
├── skills/                    # Sub-agent implementations
│   ├── web_research/
│   │   ├── SKILL.md          # Skill documentation
│   │   ├── scraper.py        # Python implementation
│   │   └── index.ts          # TypeScript interface
│   │
│   └── security_scan/
│       ├── SKILL.md          # Skill documentation
│       └── zap.py            # OWASP ZAP integration
│
└── workflows/                 # Multi-stage workflows
    └── research.md           # Research workflow definition
```

## 🚀 Quick Start

### Prerequisites

```bash
# Python dependencies
pip install requests beautifulsoup4 selenium python-owasp-zap-v2.4

# For security scanning (optional)
docker run -p 8080:8080 owasp/zap2docker-stable zap.sh -daemon \
  -host 0.0.0.0 -port 8080 -config api.key=changeme

# Node.js dependencies (for TypeScript interface)
npm install
```

### Basic Usage

#### Web Research
```python
from skills.web_research.scraper import WebResearcher

researcher = WebResearcher()
results = researcher.research("AI frameworks 2026", max_sources=20)
researcher.save_results(results)
```

#### Security Scanning
```python
from skills.security_scan.zap import SecurityScanner

scanner = SecurityScanner()
results = scanner.scan(
    target="https://testsite.example.com",
    scan_type="passive"
)
```

#### TypeScript/Node.js
```typescript
import { research } from './skills/web_research';

const results = await research("AI frameworks 2026", {
  maxSources: 20,
  depth: 2
});
```

## 🎯 Key Features

### 1. **Multi-Agent Orchestration**
- Spawn specialized sub-agents on demand
- Sequential, parallel, or conditional execution
- Automatic error handling and retry logic
- Resource management and timeouts

### 2. **Web Research Agent**
- HTTP scraping with BeautifulSoup
- JavaScript rendering with Selenium
- Parallel scraping of multiple sources
- Link following with depth limits
- Content extraction and cleaning
- Source credibility assessment

### 3. **Security Scan Agent**
- OWASP ZAP integration
- Passive & active vulnerability scanning
- Application spidering
- CVE/CWE mapping
- HTML/JSON/XML report generation
- API security testing (OpenAPI/Swagger)

### 4. **Shared Memory System**
- Session-based memory (temporary)
- Persistent memory (long-term learning)
- Inter-agent communication
- Pattern learning from successes/failures
- History tracking

### 5. **Workflow Orchestration**
- Multi-stage workflow definitions
- Conditional execution based on results
- Progress tracking and checkpoints
- Partial result handling
- Memory integration

## 📚 Configuration

### Agent Configuration (SOUL.md)
Define the main agent's identity, personality, and behavior.

### Orchestration (AGENTS.md)
Configure sub-agent registry, execution strategies, and memory management.

### Tools (TOOLS.md)
Configure external tools:
- Browser settings (Selenium/Playwright)
- HTTP client configuration
- OWASP ZAP settings
- Logging preferences
- Rate limiting

### User Preferences (USER.md)
Set default research parameters, output formats, and behavior preferences.

## 🔄 Workflows

### Research Workflow
Five-stage process for comprehensive research:
1. **Planning** - Understand goal and create strategy
2. **Gathering** - Collect data from sources (parallel)
3. **Analysis** - Process and structure information
4. **Synthesis** - Generate coherent report
5. **Security** - Optional security assessment (conditional)

See [workflows/research.md](workflows/research.md) for details.

## 🛡️ Security Considerations

### Web Research
- Respects robots.txt
- Implements rate limiting
- Polite crawling delays
- User-agent identification
- Error handling for protected sites

### Security Scanning
⚠️ **Warning**: Only scan applications you own or have explicit permission to test.

- Passive scanning (safe for production)
- Active scanning (requires authorization)
- Scope management
- Stakeholder notification
- Activity logging

## 🧠 Memory & Learning

The framework learns from experience:

**Successful Patterns**:
- "Financial sites often require JavaScript rendering" → Use Selenium
- "Domain X has high reliability" → Prioritize in future research

**Failed Attempts**:
- "Cloudflare blocked requests library" → Automatically try Selenium
- "Site Y times out" → Skip or increase timeout

**Research History**:
- Track topics researched
- Store successful source lists
- Remember credibility scores

## 📊 Output Formats

### Research Reports
- **Markdown**: Formatted report with citations
- **JSON**: Structured data for automation
- **HTML**: Web-friendly presentation

### Security Reports
- **HTML**: Detailed vulnerability report
- **JSON**: Machine-readable findings
- **XML**: Standard security format

## 🔧 Extending the Framework

### Adding New Sub-Agents

1. Create folder: `skills/my_agent/`
2. Create `SKILL.md` with frontmatter:
```yaml
---
name: my_agent
description: "Use when: doing X, Y, or Z..."
triggers:
  - keyword1
  - keyword2
---
```
3. Implement agent code: `my_agent.py`
4. Register in `AGENTS.md`
5. Add to `openclaw.json`

### Creating New Workflows

1. Create `workflows/my_workflow.md`
2. Define stages and execution flow
3. Reference sub-agents
4. Add memory integration
5. Document error handling

## 📖 Documentation

- [SOUL.md](SOUL.md) - Agent identity
- [AGENTS.md](AGENTS.md) - Orchestration guide
- [MEMORY.md](MEMORY.md) - Memory system
- [TOOLS.md](TOOLS.md) - Tool configuration
- [skills/web_research/SKILL.md](skills/web_research/SKILL.md) - Research agent docs
- [skills/security_scan/SKILL.md](skills/security_scan/SKILL.md) - Security agent docs
- [workflows/research.md](workflows/research.md) - Research workflow

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Additional sub-agents (data analysis, NLP, etc.)
- New workflows (competitive analysis, threat intelligence)
- Tool integrations (databases, APIs)
- Performance optimizations
- Documentation improvements

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **OpenClaw** - Multi-agent orchestration framework
- **OWASP ZAP** - Security scanning
- **BeautifulSoup** & **Selenium** - Web scraping
- **OpenAI/Anthropic** - AI capabilities

## 🚦 Status

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: March 24, 2026

---

## 💡 Example Use Cases

### 1. Competitive Analysis
```python
# Research competitors and assess their security
results = researcher.research(
    topic="competitor products and features",
    domains=["competitor1.com", "competitor2.com"]
)

# Then scan their webapps
scanner.scan(results['webapp_urls'], scan_type='passive')
```

### 2. Threat Intelligence
```python
# Research security vulnerabilities
results = researcher.research(
    topic="CVE-2026-XXXX analysis",
    max_sources=50
)
```

### 3. Market Research
```python
# Gather market data
results = researcher.research(
    topic="AI assistant market 2026",
    date_range=("2026-01-01", "2026-03-24")
)
```

### 4. Technology Evaluation
```python
# Research and test technologies
results = researcher.research(topic="New framework X")
# Extract demo URLs from research
scanner.scan(demo_urls, scan_type='passive')
```

---

**Built with ❤️ for autonomous research and security assessment**
