# USER.md

## User Preferences

### Default Research Settings
```yaml
research:
  max_sources: 50
  depth_level: 2  # How many links deep to follow
  save_results: true
  output_format: "markdown"  # or "json", "html"
  language_preference: "en"
```

### Security Scan Settings
```yaml
security:
  scan_intensity: "medium"  # low, medium, high
  include_passive: true
  include_active: false  # Be careful - can be intrusive
  auto_generate_report: true
  notify_on_critical: true
```

### Output Preferences
```yaml
output:
  verbosity: "normal"  # minimal, normal, detailed
  show_progress: true
  color_output: true
  save_to_file: true
  file_path: "./reports"
```

### Agent Behavior
```yaml
agent_behavior:
  auto_start_subagents: true
  require_confirmation: false  # Ask before running security scans
  parallel_execution: true
  max_concurrent_agents: 3
```

### Notifications
```yaml
notifications:
  enable: true
  types:
    - task_complete
    - error
    - critical_finding
  channels:
    - console
    # - email
    # - slack
```

### Privacy & Safety
```yaml
privacy:
  respect_robots_txt: true
  user_agent_rotation: false
  proxy_usage: false
  log_sensitive_data: false
```

### Custom Workflows
```yaml
custom_workflows:
  enabled: []
  # Add your custom workflow names here
```

## User Information

```yaml
user:
  name: null
  organization: null
  timezone: "UTC"
  language: "en"
```

## API Keys & Credentials

⚠️ **Never commit this section with real credentials!**

```yaml
credentials:
  # Add your API keys here (use environment variables in production)
  openai_api_key: null
  google_api_key: null
  zap_api_key: "changeme"
```