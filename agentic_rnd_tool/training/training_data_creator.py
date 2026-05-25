"""
Training Data Creator for OpenClaw AI Summarization
Extracts (original_content, summary) pairs from existing scraping reports
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()


class TrainingDatasetCreator:
    """
    Extract training data from successful OpenClaw scraping reports
    """
    
    def __init__(self, reports_dir: str = "../reports"):
        self.reports_dir = Path(__file__).parent.parent / "reports"
        console.print(f"[cyan]📂 Looking for reports in: {self.reports_dir}[/cyan]")
    
    def extract_training_pairs(self) -> List[Dict]:
        """
        Extract (original_content, human_summary) pairs from JSON reports
        
        Returns:
            List of training samples with quality scores
        """
        training_data = []
        
        if not self.reports_dir.exists():
            console.print(f"[red]❌ Reports directory not found: {self.reports_dir}[/red]")
            return []
        
        json_files = list(self.reports_dir.glob("*.json"))
        console.print(f"[green]Found {len(json_files)} report files[/green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Extracting training data...", total=len(json_files))
            
            for report_file in json_files:
                try:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                    
                    # Extract content from report structure
                    results = report.get('results', {})
                    web_research = results.get('web_research', {})
                    content_list = web_research.get('content', [])
                    
                    for page in content_list:
                        original = page.get('content', '')
                        ai_summary = page.get('summary', '')
                        summarized = page.get('summarized', False)
                        
                        # Only include successfully summarized pages
                        if summarized and len(original) > 200 and len(ai_summary) > 30:
                            quality = self._assess_quality(original, ai_summary)
                            
                            training_data.append({
                                'document': self._clean_text(original),
                                'summary': self._clean_text(ai_summary),
                                'source': page.get('url', 'unknown'),
                                'title': page.get('title', ''),
                                'quality': quality,
                                'original_length': len(original),
                                'summary_length': len(ai_summary),
                                'compression_ratio': len(ai_summary) / len(original)
                            })
                
                except Exception as e:
                    console.print(f"[yellow]⚠️  Error processing {report_file.name}: {e}[/yellow]")
                
                progress.update(task, advance=1)
        
        return training_data
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove null bytes and control characters
        text = text.replace('\x00', '').replace('\r', ' ').replace('\n', ' ')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _assess_quality(self, original: str, summary: str) -> str:
        """
        Quality scoring for filtering training data
        
        Returns:
            "high", "medium", or "low"
        """
        if not original or not summary:
            return "low"
        
        compression_ratio = len(summary) / len(original)
        
        # Good summaries: 5-20% of original length
        if 0.05 <= compression_ratio <= 0.20:
            quality = "high"
        elif 0.20 < compression_ratio <= 0.30:
            quality = "medium"
        elif compression_ratio < 0.05:
            quality = "low"  # Too compressed, likely lost information
        else:
            quality = "low"  # Not compressed enough
        
        # Additional quality checks
        if len(summary) < 50:
            quality = "low"  # Summary too short
        
        return quality
    
    def filter_by_quality(self, data: List[Dict], min_quality: str = "medium") -> List[Dict]:
        """
        Filter training data by quality threshold
        
        Args:
            data: Training data list
            min_quality: "high", "medium", or "low"
        
        Returns:
            Filtered training data
        """
        quality_order = {"high": 3, "medium": 2, "low": 1}
        threshold = quality_order.get(min_quality, 2)
        
        filtered = [
            sample for sample in data
            if quality_order.get(sample['quality'], 0) >= threshold
        ]
        
        console.print(f"[green]Filtered: {len(filtered)}/{len(data)} samples (>= {min_quality} quality)[/green]")
        return filtered
    
    def save_dataset(self, data: List[Dict], output_path: str = "web_summarization_training_data.json"):
        """Save training dataset to JSON file"""
        output_file = Path(output_path)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]✅ Saved {len(data)} training samples to {output_file}[/green]")
    
    def generate_statistics(self, data: List[Dict]) -> Dict:
        """Generate dataset statistics"""
        if not data:
            return {}
        
        stats = {
            'total_samples': len(data),
            'quality_distribution': {},
            'avg_original_length': sum(s['original_length'] for s in data) / len(data),
            'avg_summary_length': sum(s['summary_length'] for s in data) / len(data),
            'avg_compression_ratio': sum(s['compression_ratio'] for s in data) / len(data),
            'sources': len(set(s['source'] for s in data))
        }
        
        # Count quality distribution
        for sample in data:
            quality = sample['quality']
            stats['quality_distribution'][quality] = stats['quality_distribution'].get(quality, 0) + 1
        
        return stats


def main():
    """Main execution"""
    console.print("\n[bold cyan]🎓 OpenClaw Training Data Creator[/bold cyan]\n")
    
    # Create dataset creator
    creator = TrainingDatasetCreator()
    
    # Extract training pairs
    console.print("[cyan]Step 1: Extracting training data from reports...[/cyan]")
    training_data = creator.extract_training_pairs()
    
    if not training_data:
        console.print("[red]❌ No training data found! Run some scraping jobs first.[/red]")
        console.print("[yellow]💡 Hint: python orchestrator.py <URL> --summarize --max-sources 50[/yellow]")
        return
    
    # Filter by quality
    console.print("\n[cyan]Step 2: Filtering high-quality samples...[/cyan]")
    high_quality_data = creator.filter_by_quality(training_data, min_quality="high")
    medium_quality_data = creator.filter_by_quality(training_data, min_quality="medium")
    
    # Generate statistics
    console.print("\n[cyan]Step 3: Generating statistics...[/cyan]")
    stats = creator.generate_statistics(medium_quality_data)
    
    console.print("\n[bold]📊 Dataset Statistics:[/bold]")
    console.print(f"  Total samples: {stats['total_samples']}")
    console.print(f"  Quality distribution: {stats['quality_distribution']}")
    console.print(f"  Unique sources: {stats['sources']}")
    console.print(f"  Avg original length: {stats['avg_original_length']:.0f} chars")
    console.print(f"  Avg summary length: {stats['avg_summary_length']:.0f} chars")
    console.print(f"  Avg compression: {stats['avg_compression_ratio']*100:.1f}%")
    
    # Save datasets
    console.print("\n[cyan]Step 4: Saving datasets...[/cyan]")
    creator.save_dataset(high_quality_data, "training_data_high_quality.json")
    creator.save_dataset(medium_quality_data, "training_data_medium_quality.json")
    creator.save_dataset(training_data, "training_data_all.json")
    
    console.print("\n[bold green]✅ Training data preparation complete![/bold green]")
    console.print(f"\n[yellow]💡 Recommended: Use 'training_data_medium_quality.json' for fine-tuning[/yellow]")
    console.print(f"[dim]   Contains {len(medium_quality_data)} samples with balanced quality[/dim]\n")


if __name__ == "__main__":
    main()
