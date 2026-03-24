"""
OpenClaw Orchestrator Engine
Main coordination system for multi-agent research and security framework
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

console = Console()


class AgentOrchestrator:
    """
    Main orchestrator that coordinates sub-agents based on AGENTS.md and openclaw.json
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize the orchestrator"""
        self.base_path = base_path or Path(__file__).parent
        self.config = self._load_config()
        self.soul = self._load_soul()
        self.agents_config = self._load_agents_config()
        self.memory = self._load_memory()
        self.user_prefs = self._load_user_prefs()
        
        # Rich console initialization banner
        console.print(Panel(
            f"[bold cyan]{self.config['name']}[/bold cyan] [dim]v{self.config['version']}[/dim]\n"
            f"[yellow]Soul:[/yellow] {self.soul.get('identity', 'Research & Security Agent')}\n"
            f"[green]Agents:[/green] {len(self.config['agents'])}",
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
        
        Args:
            task: User's task/query (can be URL, search term, or command)
        console.print(f"\n[bold yellow]🎯 Task:[/bold yellow] [cyan]{task}[/cyan]parameters
            
        Returns:
            Combined results from all agents
        """
        print(f"\n🎯 Task: {task}")
        print(f"📋 Analyzing and planning execution...")
        
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
                # Import WebResearcher
                sys.path.insert(0, str(self.base_path / agent_config['path']))
                from scraper import WebResearcher
                
                researcher = WebResearcher()
                result = researcher.research(task, **kwargs)
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
  
  # Tier 1: Deep crawling (5 levels, 1000 pages)
  python orchestrator.py "https://www.nasa.gov" --depth 5 --max-sources 500
  
  # Tier 1: Disable structured data extraction
  python orchestrator.py "https://example.com" --no-structured
  
  # Tier 1: All features combined
  python orchestrator.py "https://example.com" --javascript --depth 5 --max-sources 1000
"""
    )
    
    parser.add_argument('task', nargs='+', help='Research task or URL to scrape')
    
    # Tier 1 enhancements
    parser.add_argument('-j', '--javascript', action='store_true',
                      help='Enable JavaScript rendering (Selenium) for modern SPAs')
    parser.add_argument('-d', '--depth', type=int, choices=range(1, 6), metavar='DEPTH',
                      help='Crawl depth (1-5), default: 2')
    parser.add_argument('-m', '--max-sources', type=int, metavar='NUM',
                      help='Maximum sources to scrape (default: 50, max: 1000)')
    parser.add_argument('--no-structured', action='store_true',
                      help='Disable structured data extraction (JSON-LD, Schema.org)')
    parser.add_argument('--domain-filter', action='store_true', default=True,
                      help='Stay within same domain (default: True)')
    
    # AI Summarization (FREE feature)
    parser.add_argument('-s', '--summarize', action='store_true',
                      help='Enable AI summarization (FREE - uses Hugging Face transformers)')
    parser.add_argument('--summary-length', type=int, default=150, metavar='LENGTH',
                      help='Max summary length in words (default: 150)')
    
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
    
    # Display Tier 1 features if enabled
    if args.javascript or args.depth or args.max_sources or args.no_structured or args.summarize:
        feature_panel = []
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
        
        console.print(Panel(
            '\n'.join(feature_panel),
            title="🚀 Enhanced Features Active",
            border_style="green"
        ))
    
    # Initialize orchestrator with Tier 1 config
    orchestrator = AgentOrchestrator()
    
    # Pass Tier 1 parameters to executor
    tier1_config = {
        'use_javascript': args.javascript,
        'depth': args.depth,
        'max_sources': args.max_sources,
        'extract_structured': not args.no_structured,
        'domain_filter': args.domain_filter,
        'enable_summarization': args.summarize,
        'summary_length': args.summary_length
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
    
    # Success message with Tier 1 indicator
    if any([args.javascript, args.depth, args.max_sources]):
        console.print("\n[bold green]✨ Tier 1 Enhanced Scraping Complete![/bold green]")
    else:
        console.print("\n[bold green]✨ All reports generated successfully![/bold green]")


if __name__ == "__main__":
    main()
