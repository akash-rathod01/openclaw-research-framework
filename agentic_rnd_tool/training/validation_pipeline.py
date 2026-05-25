"""
Validation Pipeline - Cross-verify fine-tuned model quality
Ensures model meets global AI standards and application requirements
"""

import json
from pathlib import Path
import sys
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from transformers import pipeline
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from custom_metrics import WebSummarizationMetrics

console = Console()


class TrainingValidator:
    """
    Validate fine-tuned model against multiple standards
    """
    
    def __init__(self, fine_tuned_path: str, baseline_model: str = "facebook/bart-large-cnn"):
        console.print("\n[cyan]📦 Loading models for validation...[/cyan]")
        
        # Load fine-tuned model
        console.print(f"[yellow]Loading fine-tuned model from: {fine_tuned_path}[/yellow]")
        try:
            self.fine_tuned = pipeline("summarization", model=fine_tuned_path, device=0 if self._has_cuda() else -1)
            console.print("[green]✓ Fine-tuned model loaded[/green]")
        except Exception as e:
            console.print(f"[red]❌ Failed to load fine-tuned model: {e}[/red]")
            raise
        
        # Load baseline model
        console.print(f"[yellow]Loading baseline model: {baseline_model}[/yellow]")
        try:
            self.baseline = pipeline("summarization", model=baseline_model, device=0 if self._has_cuda() else -1)
            console.print("[green]✓ Baseline model loaded[/green]")
        except Exception as e:
            console.print(f"[red]❌ Failed to load baseline model: {e}[/red]")
            raise
        
        # Custom metrics evaluator
        self.custom_metrics = WebSummarizationMetrics()
    
    def _has_cuda(self):
        """Check if CUDA is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def _generate_summary(self, model, text: str, max_length: int = 150) -> str:
        """Generate summary with error handling"""
        try:
            # Truncate input if too long
            if len(text) > 3000:
                text = text[:3000]
            
            result = model(text, max_length=max_length, min_length=30, do_sample=False)
            return result[0]['summary_text']
        except Exception as e:
            console.print(f"[yellow]⚠️  Summary generation error: {e}[/yellow]")
            return text[:150]  # Fallback
    
    def validate_improvement(self, test_data_path: str, num_samples: int = 50) -> dict:
        """
        Ensure fine-tuned model outperforms baseline
        
        Args:
            test_data_path: Path to test data JSON
            num_samples: Number of samples to evaluate
        
        Returns:
            Dict with comparison results
        """
        console.print(f"\n[cyan]🔍 Validating model improvement ({num_samples} samples)...[/cyan]")
        
        # Load test data
        with open(test_data_path, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        # Sample data
        test_samples = test_data[:num_samples] if len(test_data) > num_samples else test_data
        
        console.print(f"[green]Testing on {len(test_samples)} samples[/green]\n")
        
        baseline_scores = {'rouge1': [], 'rouge2': [], 'rougeL': [], 'time': []}
        finetuned_scores = {'rouge1': [], 'rouge2': [], 'rougeL': [], 'time': []}
        
        for i, sample in enumerate(test_samples, 1):
            original = sample['document']
            reference = sample['summary']
            
            console.print(f"[dim]Processing sample {i}/{len(test_samples)}...[/dim]", end='\r')
            
            # Baseline model
            start_time = time.time()
            baseline_summary = self._generate_summary(self.baseline, original)
            baseline_time = time.time() - start_time
            
            # Fine-tuned model
            start_time = time.time()
            finetuned_summary = self._generate_summary(self.fine_tuned, original)
            finetuned_time = time.time() - start_time
            
            # Calculate ROUGE scores
            from rouge_score import rouge_scorer
            scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
            
            baseline_rouge = scorer.score(reference, baseline_summary)
            finetuned_rouge = scorer.score(reference, finetuned_summary)
            
            baseline_scores['rouge1'].append(baseline_rouge['rouge1'].fmeasure)
            baseline_scores['rouge2'].append(baseline_rouge['rouge2'].fmeasure)
            baseline_scores['rougeL'].append(baseline_rouge['rougeL'].fmeasure)
            baseline_scores['time'].append(baseline_time)
            
            finetuned_scores['rouge1'].append(finetuned_rouge['rouge1'].fmeasure)
            finetuned_scores['rouge2'].append(finetuned_rouge['rouge2'].fmeasure)
            finetuned_scores['rougeL'].append(finetuned_rouge['rougeL'].fmeasure)
            finetuned_scores['time'].append(finetuned_time)
        
        console.print(" " * 60, end='\r')  # Clear progress line
        
        # Calculate improvements
        improvements = {
            'rouge1': np.mean(finetuned_scores['rouge1']) - np.mean(baseline_scores['rouge1']),
            'rouge2': np.mean(finetuned_scores['rouge2']) - np.mean(baseline_scores['rouge2']),
            'rougeL': np.mean(finetuned_scores['rougeL']) - np.mean(baseline_scores['rougeL']),
            'time': np.mean(baseline_scores['time']) - np.mean(finetuned_scores['time'])
        }
        
        # Require at least 5% improvement on ROUGE-L
        is_improved = improvements['rougeL'] > 0.05
        
        return {
            'improved': is_improved,
            'improvements': improvements,
            'baseline': {k: np.mean(v) for k, v in baseline_scores.items()},
            'finetuned': {k: np.mean(v) for k, v in finetuned_scores.items()}
        }
    
    def validate_global_standards(self, scores: dict) -> dict:
        """
        Check against published benchmark standards
        
        Args:
            scores: Dict with rouge1, rouge2, rougeL scores
        
        Returns:
            Dict with pass/fail for each metric
        """
        standards = {
            'rouge1': {'min': 0.35, 'target': 0.43, 'description': 'News summarization baseline'},
            'rouge2': {'min': 0.15, 'target': 0.21, 'description': 'Bigram overlap quality'},
            'rougeL': {'min': 0.30, 'target': 0.40, 'description': 'Sequence quality'}
        }
        
        passes = {}
        for metric, thresholds in standards.items():
            score = scores.get(metric, 0)
            passes[metric] = {
                'score': score,
                'min_passed': score >= thresholds['min'],
                'target_met': score >= thresholds['target'],
                'description': thresholds['description']
            }
        
        return passes
    
    def validate_application_requirements(self, test_data_path: str, num_samples: int = 20) -> dict:
        """
        Validate against OpenClaw-specific requirements
        
        Returns:
            Dict with application requirement results
        """
        console.print(f"\n[cyan]🎯 Validating application requirements ({num_samples} samples)...[/cyan]")
        
        # Load test data
        with open(test_data_path, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        test_samples = test_data[:num_samples] if len(test_data) > num_samples else test_data
        
        all_metrics = []
        for sample in test_samples:
            original = sample['document']
            summary = self._generate_summary(self.fine_tuned, original)
            
            metrics = self.custom_metrics.evaluate_all(original, summary)
            all_metrics.append(metrics)
        
        # Aggregate
        avg_metrics = {
            k: np.mean([m[k] for m in all_metrics if k in m])
            for k in all_metrics[0].keys()
        }
        
        # Check requirements
        requirements = {
            'compression': (0.05, 0.15),  # 85-95% compression
            'informativeness': 0.70,      # 70% info retention
            'consistency': 0.90,          # 90% factual consistency
            'overall': 0.75               # 75% overall quality
        }
        
        passes = {
            'compression': requirements['compression'][0] <= avg_metrics.get('compression_ratio', 0) <= requirements['compression'][1],
            'informativeness': avg_metrics.get('informativeness', 0) >= requirements['informativeness'],
            'consistency': avg_metrics.get('factual_consistency', 0) >= requirements['consistency'],
            'overall': avg_metrics.get('overall_score', 0) >= requirements['overall']
        }
        
        return {
            'metrics': avg_metrics,
            'requirements': requirements,
            'passes': passes,
            'all_passed': all(passes.values())
        }
    
    def full_validation_report(self, test_data_path: str) -> bool:
        """
        Complete cross-verification report
        
        Returns:
            True if model ready for production, False otherwise
        """
        console.print("\n" + "="*70)
        console.print("[bold cyan]📋 FULL VALIDATION REPORT[/bold cyan]")
        console.print("="*70 + "\n")
        
        # 1. Improvement over baseline
        console.print("[bold]1️⃣  Improvement over Baseline[/bold]")
        improvement = self.validate_improvement(test_data_path)
        
        # Create comparison table
        table = Table(title="Model Comparison")
        table.add_column("Metric", style="cyan")
        table.add_column("Baseline", style="yellow")
        table.add_column("Fine-tuned", style="green")
        table.add_column("Improvement", style="magenta")
        
        for metric in ['rouge1', 'rouge2', 'rougeL']:
            baseline_val = improvement['baseline'][metric]
            finetuned_val = improvement['finetuned'][metric]
            improvement_val = improvement['improvements'][metric]
            
            status = "✅" if improvement_val > 0.05 else "⚠️"
            table.add_row(
                metric.upper(),
                f"{baseline_val:.4f}",
                f"{finetuned_val:.4f}",
                f"{status} +{improvement_val:.4f}"
            )
        
        console.print(table)
        console.print(f"\n[{'green' if improvement['improved'] else 'yellow'}]Overall Improvement: {'✅ PASS' if improvement['improved'] else '⚠️  MARGINAL'}[/{'green' if improvement['improved'] else 'yellow'}]\n")
        
        # 2. Global AI standards
        console.print("[bold]2️⃣  Global AI Standards[/bold]")
        global_standards = self.validate_global_standards(improvement['finetuned'])
        
        standards_table = Table(title="Industry Benchmarks")
        standards_table.add_column("Metric", style="cyan")
        standards_table.add_column("Score", style="yellow")
        standards_table.add_column("Min Threshold", style="blue")
        standards_table.add_column("Status", style="green")
        
        for metric, data in global_standards.items():
            status = "✅ PASS" if data['min_passed'] else "❌ FAIL"
            standards_table.add_row(
                metric.upper(),
                f"{data['score']:.4f}",
                f"≥ {0.35 if metric == 'rouge1' else 0.15 if metric == 'rouge2' else 0.30}",
                status
            )
        
        console.print(standards_table)
        global_passed = all(d['min_passed'] for d in global_standards.values())
        console.print(f"\n[{'green' if global_passed else 'red'}]Global Standards: {'✅ PASS' if global_passed else '❌ FAIL'}[/{'green' if global_passed else 'red'}]\n")
        
        # 3. Application requirements
        console.print("[bold]3️⃣  Application Requirements[/bold]")
        app_requirements = self.validate_application_requirements(test_data_path)
        
        req_table = Table(title="OpenClaw Requirements")
        req_table.add_column("Requirement", style="cyan")
        req_table.add_column("Score", style="yellow")
        req_table.add_column("Target", style="blue")
        req_table.add_column("Status", style="green")
        
        metrics = app_requirements['metrics']
        reqs = app_requirements['requirements']
        passes = app_requirements['passes']
        
        req_table.add_row(
            "Compression Ratio",
            f"{metrics.get('compression_ratio', 0):.2%}",
            f"{reqs['compression'][0]:.0%}-{reqs['compression'][1]:.0%}",
            "✅ PASS" if passes['compression'] else "❌ FAIL"
        )
        req_table.add_row(
            "Informativeness",
            f"{metrics.get('informativeness', 0):.2f}",
            f"≥ {reqs['informativeness']:.2f}",
            "✅ PASS" if passes['informativeness'] else "❌ FAIL"
        )
        req_table.add_row(
            "Factual Consistency",
            f"{metrics.get('factual_consistency', 0):.2%}",
            f"≥ {reqs['consistency']:.0%}",
            "✅ PASS" if passes['consistency'] else "❌ FAIL"
        )
        req_table.add_row(
            "Overall Quality",
            f"{metrics.get('overall_score', 0):.2f}",
            f"≥ {reqs['overall']:.2f}",
            "✅ PASS" if passes['overall'] else "❌ FAIL"
        )
        
        console.print(req_table)
        console.print(f"\n[{'green' if app_requirements['all_passed'] else 'red'}]Application Requirements: {'✅ PASS' if app_requirements['all_passed'] else '❌ FAIL'}[/{'green' if app_requirements['all_passed'] else 'red'}]\n")
        
        # Overall verdict
        all_passed = (
            improvement['improved'] and
            global_passed and
            app_requirements['all_passed']
        )
        
        console.print("="*70)
        if all_passed:
            console.print(Panel(
                "[bold green]🎉 MODEL READY FOR PRODUCTION[/bold green]\n\n" +
                "The fine-tuned model meets all requirements:\n" +
                "✅ Outperforms baseline by >5% on ROUGE-L\n" +
                "✅ Meets global AI industry standards\n" +
                "✅ Satisfies application-specific requirements\n\n" +
                "[bold]Next Steps:[/bold]\n" +
                "1. Update skills/ai_summarization/summarizer.py\n" +
                "2. Test on live websites\n" +
                "3. Monitor performance in production",
                title="✅ VALIDATION PASSED",
                border_style="green"
            ))
        else:
            console.print(Panel(
                "[bold yellow]⚠️  MODEL NEEDS IMPROVEMENT[/bold yellow]\n\n" +
                "The model did not pass all validation checks.\n\n" +
                "[bold]Recommendations:[/bold]\n" +
                "1. Train for more epochs (try 5-7 instead of 3)\n" +
                "2. Collect more high-quality training data\n" +
                "3. Review samples with low scores\n" +
                "4. Consider data augmentation techniques",
                title="⚠️  VALIDATION INCOMPLETE",
                border_style="yellow"
            ))
        
        console.print("="*70 + "\n")
        
        return all_passed


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate fine-tuned summarization model")
    parser.add_argument(
        "--model",
        type=str,
        default="./fine_tuned_model/final",
        help="Path to fine-tuned model"
    )
    parser.add_argument(
        "--test-data",
        type=str,
        default="training_data_medium_quality.json",
        help="Path to test data JSON"
    )
    
    args = parser.parse_args()
    
    # Check if model exists
    if not Path(args.model).exists():
        console.print(f"[red]❌ Model not found: {args.model}[/red]")
        console.print("[yellow]💡 Run: python fine_tune_summarizer.py first[/yellow]\n")
        return
    
    # Check if test data exists
    if not Path(args.test_data).exists():
        console.print(f"[red]❌ Test data not found: {args.test_data}[/red]")
        console.print("[yellow]💡 Run: python training_data_creator.py first[/yellow]\n")
        return
    
    # Initialize validator
    validator = TrainingValidator(
        fine_tuned_path=args.model,
        baseline_model="facebook/bart-large-cnn"
    )
    
    # Run full validation
    passed = validator.full_validation_report(args.test_data)
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
