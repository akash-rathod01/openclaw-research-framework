"""
Fine-Tune BART Summarization Model for Web Content
Following global AI standards and best practices
Optimized for gaming laptop GPU (RTX 3060+)
"""

from transformers import (
    BartForConditionalGeneration,
    BartTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq
)
from datasets import load_dataset, Dataset
import torch
import numpy as np
from rouge_score import rouge_scorer
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel

console = Console()


class SummarizationFineTuner:
    """
    Fine-tune BART model for web content summarization
    Optimized for local GPU training
    """
    
    def __init__(
        self,
        model_name: str = "facebook/bart-large-cnn",
        output_dir: str = "./fine_tuned_model"
    ):
        self.model_name = model_name
        self.output_dir = output_dir
        
        # Check GPU availability
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        console.print(Panel(
            f"[cyan]Device: {self.device}[/cyan]\n" +
            (f"[green]GPU: {torch.cuda.get_device_name(0)}[/green]" if self.device == "cuda" else "[yellow]CPU only - training will be slower[/yellow]"),
            title="🖥️  Hardware Detection"
        ))
        
        # Load pre-trained model and tokenizer
        console.print("\n[yellow]📥 Loading pre-trained BART model...[/yellow]")
        console.print("[dim]This may take 1-2 minutes (downloading 1.6GB model)[/dim]")
        
        self.model = BartForConditionalGeneration.from_pretrained(model_name)
        self.tokenizer = BartTokenizer.from_pretrained(model_name)
        
        console.print("[green]✓ Model loaded successfully![/green]")
        
        # ROUGE scorer for evaluation
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'],
            use_stemmer=True
        )
    
    def prepare_dataset(self, data_path: str):
        """
        Prepare dataset following Hugging Face standards
        
        Args:
            data_path: Path to JSON training data file
        
        Returns:
            Dict with train/validation/test splits
        """
        console.print(f"\n[cyan]📊 Loading training data from: {data_path}[/cyan]")
        
        # Load your custom data
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        console.print(f"[green]Loaded {len(data)} training samples[/green]")
        
        # Convert to Hugging Face Dataset
        dataset = Dataset.from_dict({
            'document': [d['document'] for d in data],
            'summary': [d['summary'] for d in data]
        })
        
        # Train/Val/Test split (80/10/10)
        console.print("[cyan]Splitting dataset: 80% train, 10% validation, 10% test[/cyan]")
        
        dataset = dataset.train_test_split(test_size=0.2, seed=42)
        test_val = dataset['test'].train_test_split(test_size=0.5, seed=42)
        
        splits = {
            'train': dataset['train'],
            'validation': test_val['train'],
            'test': test_val['test']
        }
        
        console.print(f"[green]✓ Train: {len(splits['train'])} samples[/green]")
        console.print(f"[green]✓ Validation: {len(splits['validation'])} samples[/green]")
        console.print(f"[green]✓ Test: {len(splits['test'])} samples[/green]")
        
        return splits
    
    def preprocess_function(self, examples):
        """
        Tokenize inputs and targets
        """
        # Tokenize documents
        model_inputs = self.tokenizer(
            examples['document'],
            max_length=1024,  # BART max input length
            truncation=True,
            padding='max_length'
        )
        
        # Tokenize summaries
        labels = self.tokenizer(
            examples['summary'],
            max_length=256,   # Max summary length
            truncation=True,
            padding='max_length'
        )
        
        model_inputs['labels'] = labels['input_ids']
        return model_inputs
    
    def compute_metrics(self, eval_pred):
        """
        Compute evaluation metrics following global AI standards
        
        Returns:
            Dict with ROUGE scores and custom metrics
        """
        predictions, labels = eval_pred
        
        # Decode predictions
        decoded_preds = self.tokenizer.batch_decode(
            predictions,
            skip_special_tokens=True
        )
        
        # Decode labels (replace -100 with pad token)
        labels = np.where(labels != -100, labels, self.tokenizer.pad_token_id)
        decoded_labels = self.tokenizer.batch_decode(
            labels,
            skip_special_tokens=True
        )
        
        # Compute ROUGE scores (global standard for summarization)
        rouge_scores = {
            'rouge1': [],
            'rouge2': [],
            'rougeL': []
        }
        
        for pred, label in zip(decoded_preds, decoded_labels):
            scores = self.rouge_scorer.score(label, pred)
            rouge_scores['rouge1'].append(scores['rouge1'].fmeasure)
            rouge_scores['rouge2'].append(scores['rouge2'].fmeasure)
            rouge_scores['rougeL'].append(scores['rougeL'].fmeasure)
        
        # Application-specific metrics
        compression_ratios = [
            len(pred.split()) / max(len(label.split()), 1)
            for pred, label in zip(decoded_preds, decoded_labels)
        ]
        
        return {
            # Global AI Standards:
            'rouge1': np.mean(rouge_scores['rouge1']),
            'rouge2': np.mean(rouge_scores['rouge2']),
            'rougeL': np.mean(rouge_scores['rougeL']),
            
            # Application-Specific:
            'compression_ratio': np.mean(compression_ratios),
            'avg_summary_length': np.mean([len(p.split()) for p in decoded_preds])
        }
    
    def train(self, dataset_dict, num_epochs: int = 3, batch_size: int = 4):
        """
        Fine-tune the model with best practices
        Optimized for gaming laptop GPU
        
        Args:
            dataset_dict: Dict with train/validation/test datasets
            num_epochs: Number of training epochs
            batch_size: Batch size (adjust based on GPU memory)
        """
        # Preprocess datasets
        console.print("\n[cyan]🔄 Preprocessing datasets (tokenizing)...[/cyan]")
        tokenized_datasets = {
            split: dataset.map(
                self.preprocess_function,
                batched=True,
                remove_columns=dataset.column_names,
                desc=f"Tokenizing {split}"
            )
            for split, dataset in dataset_dict.items()
        }
        
        # Training arguments optimized for local GPU
        console.print("\n[cyan]⚙️  Configuring training parameters...[/cyan]")
        
        # Adjust batch size based on GPU memory
        if self.device == "cuda":
            gpu_mem_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            console.print(f"[green]GPU Memory: {gpu_mem_gb:.1f} GB[/green]")
            
            # Adjust batch size for GPU memory
            if gpu_mem_gb < 8:
                batch_size = 2
                console.print("[yellow]⚠️  Limited GPU memory - using batch_size=2[/yellow]")
            elif gpu_mem_gb < 12:
                batch_size = 4
                console.print("[green]Using batch_size=4[/green]")
            else:
                batch_size = 8
                console.print("[green]Using batch_size=8[/green]")
        else:
            batch_size = 1
            console.print("[yellow]⚠️  CPU training - using batch_size=1[/yellow]")
        
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            
            # Training hyperparameters (optimized for summarization)
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size * 2,
            learning_rate=2e-5,
            weight_decay=0.01,
            warmup_steps=500,
            
            # Evaluation strategy
            evaluation_strategy="steps",
            eval_steps=100,
            save_strategy="steps",
            save_steps=100,
            save_total_limit=3,  # Keep only best 3 checkpoints
            load_best_model_at_end=True,
            metric_for_best_model="rougeL",
            
            # Logging
            logging_dir=f'{self.output_dir}/logs',
            logging_steps=50,
            report_to="none",  # Disable W&B for local training
            
            # Performance optimization
            fp16=self.device == "cuda",  # Mixed precision only on GPU
            dataloader_num_workers=2,  # Reduce for local training
            gradient_accumulation_steps=4,  # Effective batch size = 4*batch_size
            
            # Reproducibility
            seed=42
        )
        
        # Data collator
        data_collator = DataCollatorForSeq2Seq(
            tokenizer=self.tokenizer,
            model=self.model
        )
        
        # Initialize Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_datasets['train'],
            eval_dataset=tokenized_datasets['validation'],
            tokenizer=self.tokenizer,
            data_collator=data_collator,
            compute_metrics=self.compute_metrics
        )
        
        # Train!
        console.print("\n" + "="*60)
        console.print("[bold cyan]🚀 Starting fine-tuning...[/bold cyan]")
        console.print("="*60 + "\n")
        console.print(f"[yellow]This will take 2-4 hours on GPU, 8-12 hours on CPU[/yellow]")
        console.print(f"[dim]You can close this window - training will continue[/dim]\n")
        
        trainer.train()
        
        # Final evaluation on test set
        console.print("\n[cyan]📊 Evaluating on test set...[/cyan]")
        test_results = trainer.evaluate(tokenized_datasets['test'])
        
        console.print("\n[bold green]✅ Test Results:[/bold green]")
        console.print(f"  ROUGE-1: {test_results['eval_rouge1']:.4f}")
        console.print(f"  ROUGE-2: {test_results['eval_rouge2']:.4f}")
        console.print(f"  ROUGE-L: {test_results['eval_rougeL']:.4f}")
        console.print(f"  Compression: {test_results['eval_compression_ratio']:.2%}")
        console.print(f"  Avg Length: {test_results['eval_avg_summary_length']:.0f} words")
        
        # Save final model
        console.print(f"\n[cyan]💾 Saving fine-tuned model to {self.output_dir}/final[/cyan]")
        trainer.save_model(f"{self.output_dir}/final")
        self.tokenizer.save_pretrained(f"{self.output_dir}/final")
        
        # Save test results
        with open(f"{self.output_dir}/test_results.json", 'w') as f:
            json.dump(test_results, f, indent=2)
        
        console.print(f"\n[bold green]✅ Training complete! Model saved to {self.output_dir}/final[/bold green]\n")
        
        return test_results


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fine-tune BART for web summarization")
    parser.add_argument(
        "--data",
        type=str,
        default="training_data_medium_quality.json",
        help="Path to training data JSON file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./fine_tuned_model",
        help="Output directory for fine-tuned model"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs (default: 3)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Training batch size (auto-adjusted for GPU memory)"
    )
    
    args = parser.parse_args()
    
    console.print("\n" + "="*60)
    console.print("[bold cyan]🎓 OpenClaw AI Fine-Tuning System[/bold cyan]")
    console.print("="*60 + "\n")
    
    # Check if training data exists
    if not Path(args.data).exists():
        console.print(f"[red]❌ Training data not found: {args.data}[/red]")
        console.print("[yellow]💡 Run: python training_data_creator.py first[/yellow]\n")
        return
    
    # Initialize fine-tuner
    tuner = SummarizationFineTuner(
        model_name="facebook/bart-large-cnn",
        output_dir=args.output
    )
    
    # Prepare dataset
    datasets = tuner.prepare_dataset(args.data)
    
    # Train the model
    results = tuner.train(datasets, num_epochs=args.epochs, batch_size=args.batch_size)
    
    console.print("\n" + "="*60)
    console.print("[bold green]🎉 Fine-tuning complete![/bold green]")
    console.print("="*60)
    console.print(f"\n[bold]Final ROUGE-L Score: {results['eval_rougeL']:.4f}[/bold]")
    console.print(f"\n[yellow]💡 Next steps:[/yellow]")
    console.print(f"   1. Review results in {args.output}/test_results.json")
    console.print(f"   2. Run validation: python validation_pipeline.py")
    console.print(f"   3. Update skills/ai_summarization/summarizer.py to use: {args.output}/final")
    console.print()


if __name__ == "__main__":
    main()
