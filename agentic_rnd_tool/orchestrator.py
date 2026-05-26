"""
OpenClaw Orchestrator Engine v1.1
Main coordination system for multi-agent research and security framework

NEW IN v1.1:
- Source ranking for intelligent URL prioritization
- Adaptive planning engine with decision trees
- Rule-based reasoning agent for smart decisions
"""

import json
import yaml
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import importlib.util

# Rich console output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from rich.syntax import Syntax
from rich import print as rprint

# v1.1 Enhancements
from skills.source_ranker import SourceRanker, URLScore
from planning_engine import PlanningEngine, ExecutionGoal, ExecutionState
from skills.reasoning_agent import ReasoningAgent, ReasoningContext, Decision

console = Console()


class AgentOrchestrator:
    """
    Main orchestrator that coordinates sub-agents based on AGENTS.md and openclaw.json
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize the orchestrator with v1.1 enhancements"""
        self.base_path = base_path or Path(__file__).parent
        self.config = self._load_config()
        self.soul = self._load_soul()
        self.agents_config = self._load_agents_config()
        self.memory = self._load_memory()
        self.user_prefs = self._load_user_prefs()
        
        # v1.1: Initialize new intelligent systems
        self.source_ranker = SourceRanker()
        self.reasoning_agent = ReasoningAgent()
        self.planner = None  # Initialize per-task with specific goal
        
        # Track v1.1 feature usage
        self.v11_stats = {
            'urls_ranked': 0,
            'decisions_made': 0,
            'plans_created': 0
        }
        
        # Rich console initialization banner
        console.print(Panel(
            f"[bold cyan]{self.config['name']}[/bold cyan] [dim]v1.1.0[/dim]\n"
            f"[yellow]Soul:[/yellow] {self.soul.get('identity', 'Research & Security Agent')}\n"
            f"[green]Agents:[/green] {len(self.config['agents'])}\n"
            f"[magenta]✨ NEW:[/magenta] Source Ranking • Planning Engine • Reasoning Agent",
            title="🤖 OpenClaw Orchestrator",
            border_style="cyan"
        ))
        
    def _load_config(self) -> Dict:
        """Load openclaw.json configuration"""
        config_path = self.base_path / 'openclaw.json'
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Warning: Could not load openclaw.json: {e}")
            return {"name": "Orchestrator", "version": "1.0.0", "agents": []}
    
    def _load_soul(self) -> Dict:
        """Load agent identity from SOUL.md"""
        soul_path = self.base_path / 'SOUL.md'
        try:
            with open(soul_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return {
                    'identity': 'Autonomous Research & Security Agent',
                    'content': content
                }
        except Exception as e:
            return {'identity': 'Agent', 'content': ''}
    
    def _load_agents_config(self) -> Dict:
        """Load agent configuration from AGENTS.md"""
        agents_path = self.base_path / 'AGENTS.md'
        try:
            with open(agents_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Parse YAML frontmatter if present
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        return yaml.safe_load(parts[1])
                return {}
        except Exception as e:
            return {}
    
    def _load_memory(self) -> Dict:
        """Load shared memory"""
        return {
            'session_id': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'start_time': datetime.now().isoformat(),
            'research_history': [],
            'security_scans': [],
            'learned_patterns': []
        }
    
    def _load_user_prefs(self) -> Dict:
        """Load user preferences"""
        return {
            'max_sources': 50,
            'scan_type': 'passive',
            'output_format': 'markdown'
        }
    
    def execute(self, task: str, **kwargs) -> Dict:
        """
        Main execution entry point - analyzes task and dispatches to appropriate agents
        
        v1.1: Now uses Planning Engine and Reasoning Agent for intelligent execution
        
        Args:
            task: User's task/query (can be URL, search term, or command)
            **kwargs: Additional parameters
            
        Returns:
            Combined results from all agents
        """
        console.print(f"\n[bold yellow]🎯 Task:[/bold yellow] [cyan]{task}[/cyan]")
        
        # v1.1: Initialize planning engine with goal
        goal = ExecutionGoal(
            goal_type=kwargs.get('goal_type', 'comprehensive'),
            target_sources=kwargs.get('max_sources', 50),
            max_depth=kwargs.get('depth', 3),
            require_summarization=kwargs.get('enable_summarization', False),
            prioritize_authority=True
        )
        
        self.planner = PlanningEngine(goal)
        self.v11_stats['plans_created'] += 1
        
        console.print(f"[dim]🧠 Planning execution with goal: {goal.goal_type}[/dim]")
        
        # Determine which agents to activate
        agents_to_run = self._plan_execution(task, **kwargs)
        
        # Execute agents
        results = {
            'task': task,
            'timestamp': datetime.now().isoformat(),
            'agents_used': [],
            'results': {}
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            for agent_info in agents_to_run:
                agent_id = agent_info['id']
                agent_config = agent_info['config']
                
                task_progress = progress.add_task(
                    f"[cyan]🚀 {agent_config['name']}...", 
                    total=None
                )
                
                result = self._spawn_agent(agent_id, task, **kwargs)
                
                results['agents_used'].append(agent_config['name'])
                results['results'][agent_id] = result
                
                progress.update(task_progress, completed=True)
                console.print(f"[green]✓ {agent_config['name']} completed[/green]")
        
        # AI Summarization (if enabled)
        if kwargs.get('enable_summarization', False):
            console.print("\n[magenta]🤖 AI Summarization enabled - processing results...[/magenta]")
            
            # Check if web_research produced results
            if 'web_research' in results['results']:
                web_data = results['results']['web_research']
                sources = web_data.get('content', [])
                
                if sources:
                    try:
                        # Import and run AI summarization agent
                        sys.path.insert(0, str(self.base_path / 'skills' / 'ai_summarization'))
                        from summarizer import research as ai_summarize
                        
                        summary_result = ai_summarize(
                            task,
                            sources=sources,
                            max_length=kwargs.get('summary_length', 150),
                            min_length=50
                        )
                        
                        if summary_result.get('success'):
                            # Update web_research results with summarized sources
                            results['results']['web_research']['content'] = summary_result['sources']
                            results['results']['web_research']['ai_summarized'] = True
                            results['results']['web_research']['summarization_stats'] = {
                                'total_sources': summary_result['total_sources'],
                                'summarized_count': summary_result['summarized_count'],
                                'model': summary_result['model']
                            }
                            results['agents_used'].append('AI Summarization')
                            
                        else:
                            console.print(f"[yellow]⚠️  AI summarization failed: {summary_result.get('error')}[/yellow]")
                            
                    except ImportError as e:
                        console.print(f"[red]❌ AI Summarization not installed: {e}[/red]")
                        console.print("[yellow]💡 Install with: pip install transformers torch[/yellow]")
                    except Exception as e:
                        console.print(f"[yellow]⚠️  AI Summarization error: {e}[/yellow]")
                else:
                    console.print("[dim]No sources to summarize[/dim]")
        
        # Synthesize results
        final_result = self._synthesize_results(results)
        
        # v1.1: Display intelligent systems usage
        if any(self.v11_stats.values()):
            console.print("\n[bold magenta]✨ v1.1 Intelligent Systems Report:[/bold magenta]")
            stats_table = Table(border_style="magenta", show_header=False)
            stats_table.add_column("Feature", style="cyan")
            stats_table.add_column("Usage", style="yellow", justify="right")
            
            if self.v11_stats['urls_ranked'] > 0:
                stats_table.add_row("🎯 URLs Ranked", str(self.v11_stats['urls_ranked']))
            if self.v11_stats['decisions_made'] > 0:
                stats_table.add_row("🧠 Reasoning Decisions", str(self.v11_stats['decisions_made']))
            if self.v11_stats['plans_created'] > 0:
                stats_table.add_row("📋 Execution Plans", str(self.v11_stats['plans_created']))
            
            console.print(stats_table)
        
        # Update memory
        self._update_memory(task, final_result)
        
        return final_result
    
    def _plan_execution(self, task: str, **kwargs) -> List[Dict]:
        """
        Intelligently determine which agents to activate
        """
        agents_to_run = []
        task_lower = task.lower()
        
        # Check each agent's triggers
        for agent in self.config.get('agents', []):
            triggers = agent.get('triggers', [])
            
            # Check if any trigger matches
            if any(trigger in task_lower for trigger in triggers):
                agents_to_run.append({
                    'id': agent['id'],
                    'config': agent
                })
            # Always run web_research for URLs
            elif (task.startswith('http://') or task.startswith('https://')) and agent['id'] == 'web_research':
                agents_to_run.append({
                    'id': agent['id'],
                    'config': agent
                })
        
        # Default to web_research if no matches
        if not agents_to_run:
            for agent in self.config.get('agents', []):
                if agent['id'] == 'web_research':
                    agents_to_run.append({
                        'id': agent['id'],
                        'config': agent
                    })
                    break
        
        # Display execution plan in a table
        table = Table(title="📊 Execution Plan", border_style="green")
        table.add_column("Agent", style="cyan")
        table.add_column("Role", style="yellow")
        table.add_column("Status", style="green")
        
        for a in agents_to_run:
            table.add_row(
                a['config']['name'],
                a['config'].get('description', 'No description')[:50],
                "✓ Ready"
            )
        
        console.print(table)
        
        return agents_to_run
    
    def _spawn_agent(self, agent_id: str, task: str, **kwargs) -> Dict:
        """
        Spawn and execute a sub-agent
        
        v1.1: Integrates source ranking and reasoning agent for web_research
        """
        # Find agent configuration
        agent_config = None
        for agent in self.config.get('agents', []):
            if agent['id'] == agent_id:
                agent_config = agent
                break
        
        if not agent_config:
            return {'error': f'Agent {agent_id} not found'}
        
        try:
            # Import the agent module
            agent_path = self.base_path / agent_config['path'] / agent_config['entry_point']
            
            if agent_id == 'web_research':
                # v1.1: Use reasoning agent to decide if URL should be scraped
                reasoning_context = ReasoningContext(
                    url=task,
                    depth=0,
                    sources_collected=0,
                    target_sources=kwargs.get('max_sources', 50)
                )
                
                decision = self.reasoning_agent.should_scrape_url(reasoning_context)
                self.v11_stats['decisions_made'] += 1
                
                console.print(f"[dim]🧠 Reasoning: {decision.reasoning[:80]}...[/dim]")
                
                if decision.decision == Decision.SKIP:
                    console.print(f"[yellow]⚠️  Reasoning agent skipped URL[/yellow]")
                    return {
                        'skipped': True,
                        'reason': decision.reasoning,
                        'sources_scraped': 0,
                        'content': []
                    }
                
                # Import WebResearcher
                sys.path.insert(0, str(self.base_path / agent_config['path']))
                from scraper import WebResearcher
                
                researcher = WebResearcher()
                result = researcher.research(task, **kwargs)
                
                # v1.1: Apply source ranking to discovered URLs
                if 'urls' in result and result['urls']:
                    console.print(f"[dim]🎯 Ranking {len(result['urls'])} discovered URLs...[/dim]")
                    
                    ranked_urls = self.source_ranker.rank_sources(result['urls'], context=task)
                    self.v11_stats['urls_ranked'] += len(result['urls'])
                    
                    # Update result with ranked URLs
                    result['urls_ranked'] = [score.url for score in ranked_urls[:20]]  # Top 20
                    result['ranking_report'] = f"Ranked {len(ranked_urls)} URLs by authority and relevance"
                    
                    # Show top 3 ranked URLs
                    if ranked_urls:
                        console.print("[dim]🏆 Top ranked URLs:[/dim]")
                        for idx, score in enumerate(ranked_urls[:3], 1):
                            console.print(f"[dim]  {idx}. {score.url} (score: {score.total_score:.2f})[/dim]")
                
                return result
                
            elif agent_id == 'security_scan':
                # Import SecurityScanner
                sys.path.insert(0, str(self.base_path / agent_config['path']))
                try:
                    from zap import SecurityScanner
                    scanner = SecurityScanner()
                    result = scanner.scan(task, **kwargs)
                    return result
                except ModuleNotFoundError:
                    return {
                        'error': 'ZAP library not installed',
                        'message': 'Install with: pip install python-owasp-zap-v2.4'
                    }
            
            else:
                return {'error': f'Unknown agent type: {agent_id}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _synthesize_results(self, results: Dict) -> Dict:
        """
        Combine results from multiple agents into coherent output
        """
        synthesis = {
            'task': results['task'],
            'timestamp': results['timestamp'],
            'agents_used': results['agents_used'],
            'summary': '',
            'data': {}
        }
        
        # Process web research results
        if 'web_research' in results['results']:
            web_data = results['results']['web_research']
            synthesis['data']['research'] = {
                'sources_scraped': web_data.get('sources_scraped', 0),
                'content_items': len(web_data.get('content', [])),
                'summary': web_data.get('summary', '')
            }
        
        # Process security scan results
        if 'security_scan' in results['results']:
            sec_data = results['results']['security_scan']
            if 'error' not in sec_data:
                synthesis['data']['security'] = {
                    'alerts': len(sec_data.get('alerts', [])),
                    'summary': sec_data.get('summary', {})
                }
        
        # Generate overall summary
        summary_parts = []
        if 'research' in synthesis['data']:
            summary_parts.append(f"Researched {synthesis['data']['research']['sources_scraped']} sources")
        if 'security' in synthesis['data']:
            summary_parts.append(f"Found {synthesis['data']['security']['alerts']} security alerts")
        
        synthesis['summary'] = '. '.join(summary_parts) if summary_parts else 'Task completed'
        synthesis['raw_results'] = results['results']
        
        # Display results summary in a rich panel
        self._display_results_summary(synthesis)
        
        return synthesis
    
    def _display_results_summary(self, synthesis: Dict):
        """Display a beautiful summary of results"""
        
        # Create results table
        table = Table(title="📊 Results Summary", border_style="cyan")
        table.add_column("Category", style="yellow", no_wrap=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green", justify="right")
        
        # Add research results
        if 'research' in synthesis['data']:
            table.add_row(
                "🔍 Research",
                "Sources Scraped",
                str(synthesis['data']['research']['sources_scraped'])
            )
            table.add_row(
                "",
                "Content Items",
                str(synthesis['data']['research']['content_items'])
            )
        
        # Add security results
        if 'security' in synthesis['data']:
            table.add_row(
                "🔒 Security",
                "Total Alerts",
                str(synthesis['data']['security']['alerts'])
            )
            summary = synthesis['data']['security'].get('summary', {})
            if summary:
                table.add_row("", "Critical", str(summary.get('critical', 0)))
                table.add_row("", "High", str(summary.get('high', 0)))
                table.add_row("", "Medium", str(summary.get('medium', 0)))
        
        console.print("\n")
        console.print(table)
        
        # Overall summary panel
        console.print("\n")
        console.print(Panel(
            f"[bold green]{synthesis['summary']}[/bold green]\n\n"
            f"[cyan]Agents Used:[/cyan] {', '.join(synthesis['agents_used'])}",
            title="✨ Task Complete",
            border_style="green"
        ))
    
    def _update_memory(self, task: str, result: Dict):
        """
        Update shared memory with task results
        """
        self.memory['research_history'].append({
            'task': task,
            'timestamp': datetime.now().isoformat(),
            'summary': result.get('summary', '')
        })
        
        console.print(f"\n[dim]💾 Memory updated: {len(self.memory['research_history'])} tasks in history[/dim]")
    
    def _update_memory(self, task: str, result: Dict):
        """
        Update shared memory with task results
        """
        self.memory['research_history'].append({
            'task': task,
            'timestamp': datetime.now().isoformat(),
            'summary': result.get('summary', '')
        })
        
        print(f"\n💾 Memory updated: {len(self.memory['research_history'])} tasks in history")


def main():
    """CLI interface for the orchestrator with Tier 1 enhancements"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Agentic RnD Tool - Multi-agent research and security framework (Tier 1 Enhanced)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (backwards compatible)
  python orchestrator.py "https://www.nasa.gov"
  
  # Tier 1: JavaScript rendering for React/Vue/Angular apps
  python orchestrator.py "https://spa-app.com" --javascript
  
  # Tier 1: Deep crawling (10 levels, 2000 pages)
  python orchestrator.py "https://www.nasa.gov" --depth 10 --max-sources 2000
  
  # Tier 1: Disable structured data extraction
  python orchestrator.py "https://example.com" --no-structured
  
  # Tier 1: All features combined (max depth, 5000 pages)
  python orchestrator.py "https://example.com" --javascript --depth 10 --max-sources 5000
"""
    )
    
    parser.add_argument('task', nargs='+', help='Research task or URL to scrape')
    
    # Tier 1 enhancements
    parser.add_argument('-j', '--javascript', action='store_true',
                      help='Enable JavaScript rendering (Selenium) for modern SPAs')
    parser.add_argument('-d', '--depth', type=int, choices=range(1, 11), metavar='DEPTH',
                      help='Crawl depth (1-10), default: 2')
    parser.add_argument('-m', '--max-sources', type=int, metavar='NUM',
                      help='Maximum sources to scrape (default: 50, max: 5000)')
    parser.add_argument('--no-structured', action='store_true',
                      help='Disable structured data extraction (JSON-LD, Schema.org)')
    parser.add_argument('--domain-filter', action='store_true', default=True,
                      help='Stay within same domain (default: True)')
    
    # AI Summarization (FREE feature)
    parser.add_argument('-s', '--summarize', action='store_true',
                      help='Enable AI summarization (FREE - uses Hugging Face transformers)')
    parser.add_argument('--summary-length', type=int, default=150, metavar='LENGTH',
                      help='Max summary length in words (default: 150)')
    
    # TIER 2: AI Content Extraction
    parser.add_argument('--extract-entities', action='store_true',
                      help='TIER 2: Extract named entities (people, orgs, locations)')
    parser.add_argument('--sentiment', action='store_true',
                      help='TIER 2: Analyze sentiment of content')
    
    # TIER 2: Anti-Bot Evasion
    parser.add_argument('--rotate-ua', action='store_true',
                      help='TIER 2: Rotate user agents to avoid detection')
    parser.add_argument('--stealth', action='store_true',
                      help='TIER 2: Enable stealth mode (advanced anti-bot headers)')
    
    # TIER 2: Multi-Modal Content
    parser.add_argument('--download-images', action='store_true',
                      help='TIER 2: Download and analyze images from pages')
    parser.add_argument('--ocr', action='store_true',
                      help='TIER 2: Perform OCR on downloaded images')
    parser.add_argument('--extract-pdfs', action='store_true',
                      help='TIER 2: Extract text from PDF files')
    
    # Check for backwards compatibility (simple usage without flags)
    if len(sys.argv) < 2:
        parser.print_help()
        console.print("\n[yellow]💡 Tip:[/yellow] Try: python orchestrator.py \"https://www.nasa.gov\"")

        return
    
    # Handle backwards compatibility - if first arg doesn't start with -, parse old way
    if not any(arg.startswith('-') for arg in sys.argv[1:]):
        # Legacy mode: all args are the task
        task = ' '.join(sys.argv[1:])
        args = argparse.Namespace(
            task=[task], 
            javascript=False, 
            depth=None, 
            max_sources=None,
            no_structured=False,
            domain_filter=True,
            summarize=False,
            summary_length=150
        )
    else:
        # New mode: parse arguments properly
        args = parser.parse_args()
    
    task = ' '.join(args.task)
    
    # Check if any Tier 2 features are enabled
    tier2_enabled = (
        getattr(args, 'extract_entities', False) or
        getattr(args, 'sentiment', False) or
        getattr(args, 'rotate_ua', False) or
        getattr(args, 'stealth', False) or
        getattr(args, 'download_images', False) or
        getattr(args, 'ocr', False) or
        getattr(args, 'extract_pdfs', False)
    )
    
    # Display Tier 1 & Tier 2 features if enabled
    if args.javascript or args.depth or args.max_sources or args.no_structured or args.summarize or tier2_enabled:
        feature_panel = []
        
        # Tier 1 features
        if args.javascript:
            feature_panel.append("[cyan]🌐 JavaScript Rendering:[/cyan] Enabled (Selenium)")
        if args.depth:
            feature_panel.append(f"[cyan]🔗 Crawl Depth:[/cyan] {args.depth} levels")
        if args.max_sources:
            feature_panel.append(f"[cyan]📊 Max Sources:[/cyan] {args.max_sources}")
        if args.no_structured:
            feature_panel.append("[yellow]⚠️  Structured Data:[/yellow] Disabled")
        else:
            feature_panel.append("[green]✨ Structured Data:[/green] Enabled (JSON-LD, Schema.org)")
        if args.summarize:
            feature_panel.append(f"[magenta]🤖 AI Summarization:[/magenta] Enabled (max {args.summary_length} words, FREE)")
        
        # Tier 2 features  
        if tier2_enabled:
            feature_panel.append("")  # Separator
            feature_panel.append("[bold green]═══ TIER 2 PROFESSIONAL FEATURES ═══[/bold green]")
            
        if getattr(args, 'extract_entities', False):
            feature_panel.append("[green]👤 Entity Extraction:[/green] Enabled (NER)")
        if getattr(args, 'sentiment', False):
            feature_panel.append("[green]😊 Sentiment Analysis:[/green] Enabled")
        if getattr(args, 'rotate_ua', False):
            feature_panel.append("[green]🔄 User-Agent Rotation:[/green] Enabled")
        if getattr(args, 'stealth', False):
            feature_panel.append("[green]🥷 Stealth Mode:[/green] Enabled")
        if getattr(args, 'download_images', False):
            feature_panel.append("[green]🖼️  Image Download:[/green] Enabled")
        if getattr(args, 'ocr', False):
            feature_panel.append("[green]📸 OCR:[/green] Enabled")
        if getattr(args, 'extract_pdfs', False):
            feature_panel.append("[green]📄 PDF Extraction:[/green] Enabled")
        
        console.print(Panel(
            '\n'.join(feature_panel),
            title="🚀 Tier 1 Enhanced Features Active" if not tier2_enabled else "🚀 Tier 1 + Tier 2 Professional Features Active",
            border_style="cyan" if not tier2_enabled else "green"
        ))
    
    # Initialize orchestrator with Tier 1 config
    orchestrator = AgentOrchestrator()
    
    # Pass Tier 1 + Tier 2 parameters to executor
    tier1_config = {
        'use_javascript': args.javascript,
        'depth': args.depth,
        'max_sources': args.max_sources,
        'extract_structured': not args.no_structured,
        'domain_filter': args.domain_filter,
        'enable_summarization': args.summarize,
        'summary_length': args.summary_length,
        # TIER 2: AI Content Extraction
        'extract_entities': getattr(args, 'extract_entities', False),
        'sentiment_analysis': getattr(args, 'sentiment', False),
        'ai_summarize': getattr(args, 'extract_entities', False) or args.summarize,  # Enable if either is set
        # TIER 2: Anti-Bot Evasion
        'rotate_user_agents': getattr(args, 'rotate_ua', False),
        'stealth_mode': getattr(args, 'stealth', False),
        # TIER 2: Multi-Modal Content
        'download_images': getattr(args, 'download_images', False),
        'ocr_images': getattr(args, 'ocr', False),
        'extract_pdf_text': getattr(args, 'extract_pdfs', False)
    }
    
    # Execute task with Tier 1 enhancements
    result = orchestrator.execute(task, **tier1_config)
    
    # Generate reports
    from report_generator import ReportGenerator
    import webbrowser
    import os
    
    reporter = ReportGenerator()
    
    # Save JSON report
    json_file = reporter.generate_json_report(result)
    console.print(f"\n[dim]💾 JSON report saved: {json_file}[/dim]")
    
    # Generate Markdown report
    md_file = reporter.generate_markdown_report(result)
    console.print(f"[dim]📄 Markdown report saved: {md_file}[/dim]")
    
    # Generate HTML Dashboard
    html_file = reporter.generate_html_report(result)
    console.print(f"[dim]🌐 HTML dashboard saved: {html_file}[/dim]")
    
    # Open HTML in browser automatically
    html_path = os.path.abspath(html_file)
    console.print(f"\n[bold cyan]🚀 Opening dashboard in browser...[/bold cyan]")
    webbrowser.open(f'file:///{html_path}')
    
    # Success message with Tier indicator
    if tier2_enabled:
        console.print("\n[bold green]✨🔥 Tier 2 Professional Scraping Complete![/bold green]")
    elif any([args.javascript, args.depth, args.max_sources]):
        console.print("\n[bold green]✨ Tier 1 Enhanced Scraping Complete![/bold green]")
    else:
        console.print("\n[bold green]✨ All reports generated successfully![/bold green]")


if __name__ == "__main__":
    main()
