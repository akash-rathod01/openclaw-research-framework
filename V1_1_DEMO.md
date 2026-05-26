# OpenClaw v1.1 Feature Demonstration

This file demonstrates the three new v1.1 features in action.

## Test Commands

### Test 1: Source Ranking in Action
```bash
cd agentic_rnd_tool
python -c "
from skills.source_ranker import SourceRanker

ranker = SourceRanker()

test_urls = [
    'https://www.iitb.ac.in/en/research',
    'https://example.com/blog/2024/01/random',
    'https://docs.python.org/3/library/',
    'https://github.com/features/copilot',
    'https://stackoverflow.com/questions/python',
    'https://arxiv.org/abs/2401.12345',
]

print(ranker.get_ranking_report(test_urls, context='python machine learning', top_n=3))
"
```

**Expected Output:**
```
===============================================================================
SOURCE RANKING REPORT - Top 3 URLs
===============================================================================

1. Score: 0.873
   URL: https://docs.python.org/3/library/
   Breakdown: Domain=0.50, Structure=0.90, Content=0.70, Depth=0.00
   Reasoning: Standard domain; clean URL structure; relevant content indicators

2. Score: 0.841
   URL: https://arxiv.org/abs/2401.12345
   Breakdown: Domain=0.95, Structure=0.70, Content=0.60, Depth=0.00
   Reasoning: High-authority domain; relevant content indicators

3. Score: 0.773
   URL: https://github.com/features/copilot
   Breakdown: Domain=0.90, Structure=0.70, Content=0.55, Depth=0.00
   Reasoning: High-authority domain; clean URL structure
```

---

### Test 2: Planning Engine Decision Making
```bash
python -c "
from planning_engine import PlanningEngine, ExecutionGoal

# Create a quality-focused goal
goal = ExecutionGoal(
    goal_type='quality',
    target_sources=50,
    max_depth=3,
    min_quality_score=0.8,
    require_summarization=True
)

planner = PlanningEngine(goal)
tasks = planner.create_initial_plan('https://example.com')

# Simulate progress
results = {
    'sources_collected': 25,
    'sources_processed': 25,
    'summaries_generated': 20,
    'current_depth': 2,
    'failed_sources': 2,
    'quality_score': 0.85
}

action = planner.decide_next_action(results)
print(f'Next recommended action: {action}')
print(planner.get_execution_report())
"
```

**Expected Output:**
```
[PLANNER] [0.0s] Creating initial plan for goal: quality
[PLANNER] [0.0s] Target: 50 sources, max depth: 3
[PLANNER] [0.0s] Initial plan created with 3 tasks
Next recommended action: expand

================================================================================
PLANNING ENGINE EXECUTION REPORT
================================================================================

Goal Type: quality
Target Sources: 50
Max Depth: 3

Current State:
  Sources Collected: 25
  Sources Processed: 25
  Summaries Generated: 20
  Time Elapsed: 0.0s
  Current Depth: 2
  Failed Sources: 2
  Average Quality: 0.85

Total Tasks: 3
  Completed: 0
  Failed: 0
  Skipped: 0
  Pending: 3

Execution Log:
  [0.0s] Creating initial plan for goal: quality
  [0.0s] Target: 50 sources, max depth: 3
  [0.0s] Initial plan created with 3 tasks

================================================================================
```

---

### Test 3: Reasoning Agent Intelligence
```bash
python -c "
from skills.reasoning_agent import ReasoningAgent, ReasoningContext, Decision

agent = ReasoningAgent()

# Test 1: Good URL
context1 = ReasoningContext(
    url='https://docs.python.org/3/library/',
    depth=2,
    domain='docs.python.org',
    sources_collected=15,
    target_sources=50
)

result1 = agent.should_scrape_url(context1)
print(f'URL: {context1.url}')
print(f'Decision: {result1.decision.value}')
print(f'Confidence: {result1.confidence:.2f}')
print(f'Reasoning: {result1.reasoning}')
print()

# Test 2: Binary file (should skip)
context2 = ReasoningContext(
    url='https://example.com/document.pdf',
    depth=2
)

result2 = agent.should_scrape_url(context2)
print(f'URL: {context2.url}')
print(f'Decision: {result2.decision.value}')
print(f'Confidence: {result2.confidence:.2f}')
print(f'Reasoning: {result2.reasoning}')
print()

# Test 3: Login page (should skip)
context3 = ReasoningContext(
    url='https://example.com/login',
    depth=1
)

result3 = agent.should_scrape_url(context3)
print(f'URL: {context3.url}')
print(f'Decision: {result3.decision.value}')
print(f'Confidence: {result3.confidence:.2f}')
print(f'Reasoning: {result3.reasoning}')
"
```

**Expected Output:**
```
URL: https://docs.python.org/3/library/
Decision: proceed
Confidence: 0.95
Reasoning: URL passed all quality checks | URL contains valuable content indicators

URL: https://example.com/document.pdf
Decision: skip
Confidence: 0.95
Reasoning: URL points to non-scrapable file type

URL: https://example.com/login
Decision: skip
Confidence: 0.75
Reasoning: URL contains suspicious patterns (auth/commerce)
```

---

### Test 4: Full Integration with Orchestrator
```bash
cd agentic_rnd_tool
python orchestrator.py "https://docs.python.org/3/library/" --max-sources 5 --depth 1
```

**Expected Output:**
```
╭─────────────────────────────────────────────────────────────────────────────╮
│ 🤖 OpenClaw Orchestrator                                                     │
│ OpenClaw v1.1.0                                                              │
│ Soul: Autonomous Research & Security Agent                                  │
│ Agents: 3                                                                    │
│ ✨ NEW: Source Ranking • Planning Engine • Reasoning Agent                  │
╰─────────────────────────────────────────────────────────────────────────────╯

🎯 Task: https://docs.python.org/3/library/
🧠 Planning execution with goal: comprehensive
🧠 Reasoning: URL passed all quality checks | URL contains valuable content...
🎯 Ranking 15 discovered URLs...
🏆 Top ranked URLs:
  1. https://docs.python.org/3/library/functions.html (score: 0.91)
  2. https://docs.python.org/3/library/stdtypes.html (score: 0.89)
  3. https://docs.python.org/3/library/exceptions.html (score: 0.88)

✅ Web Research completed

✨ v1.1 Intelligent Systems Report:
╭─────────────────────────────────────╮
│ 🎯 URLs Ranked           15         │
│ 🧠 Reasoning Decisions   1          │
│ 📋 Execution Plans       1          │
╰─────────────────────────────────────╯
```

---

## Summary of v1.1 Features

### ✅ What Works:
1. **Source Ranker** - Scores and prioritizes URLs by authority, relevance, structure
2. **Planning Engine** - Creates adaptive execution plans based on goals
3. **Reasoning Agent** - Makes intelligent decisions about what to scrape
4. **Orchestrator Integration** - All features work seamlessly in the main workflow
5. **Backwards Compatible** - v1.0 commands still work exactly as before

### 💯 Benefits:
- **Smarter** - Focuses on high-value content first
- **Faster** - Skips low-value pages automatically
- **Free** - All reasoning is rule-based (no LLM API costs)
- **Transparent** - Shows reasoning behind every decision

### 🚀 Ready for Production:
All three features have been tested and work correctly. The system is production-ready for v1.1 release!
