"""
AI Summarization Agent - FREE Version
Uses Hugging Face transformers for local, zero-cost summarization
"""

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from typing import List, Dict, Optional
from rich.console import Console

console = Console()

class AISummarizer:
    """
    AI-powered text summarization using Hugging Face transformers.
    FREE version - runs locally with no API costs.
    """
    
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        """
        Initialize the summarizer.
        
        Args:
            model_name: Hugging Face model to use. Options:
                - facebook/bart-large-cnn (best for web content - default)
                - t5-base (general purpose)
                - google/pegasus-xsum (extreme summarization)
        """
        self.model_name = model_name
        self.pipeline = None
        self._initialized = False
    
    def _lazy_load(self):
        """Lazy load the model only when first needed (saves memory)."""
        if self._initialized:
            return
        
        try:
            from transformers import pipeline
            
            console.print(f"[yellow]⏳ Loading AI model: {self.model_name}...[/yellow]")
            console.print("[dim]This may take 30-60 seconds on first run (downloading model)[/dim]")
            
            # Load the summarization pipeline
            self.pipeline = pipeline(
                "summarization",
                model=self.model_name,
                device=-1  # Use CPU (set to 0 for GPU if available)
            )
            
            self._initialized = True
            console.print(f"[green]✓ AI model loaded successfully![/green]")
            
        except ImportError:
            console.print("[red]❌ Error: 'transformers' library not installed![/red]")
            console.print("[yellow]Install with: pip install transformers torch[/yellow]")
            raise
        except Exception as e:
            console.print(f"[red]❌ Failed to load AI model: {e}[/red]")
            raise
    
    def summarize(
        self,
        text: str,
        max_length: int = 150,
        min_length: int = 50,
        do_sample: bool = False
    ) -> Optional[str]:
        """
        Summarize a single text.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length in words
            min_length: Minimum summary length in words
            do_sample: Use sampling (more creative but less consistent)
        
        Returns:
            Summary string or None if failed
        """
        if not text or len(text.strip()) < 100:
            return text  # Too short to summarize
        
        self._lazy_load()
        
        try:
            # Truncate input to model's max length (1024 tokens ~= 3000 chars)
            max_input_chars = 3000
            if len(text) > max_input_chars:
                text = text[:max_input_chars] + "..."
            
            # Generate summary
            result = self.pipeline(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=do_sample,
                truncation=True
            )
            
            return result[0]['summary_text']
            
        except Exception as e:
            console.print(f"[yellow]⚠️  Summarization failed: {e}[/yellow]")
            return None
    
    def summarize_batch(
        self,
        sources: List[Dict],
        max_length: int = 150,
        min_length: int = 50
    ) -> List[Dict]:
        """
        Summarize multiple sources in batch.
        
        Args:
            sources: List of source dictionaries with 'content' key
            max_length: Maximum summary length
            min_length: Minimum summary length
        
        Returns:
            Sources with added 'summary' key
        """
        self._lazy_load()
        
        console.print(f"[cyan]📝 Generating AI summaries for {len(sources)} sources...[/cyan]")
        
        summarized = []
        for i, source in enumerate(sources, 1):
            content = source.get('content', '')
            
            if not content or len(content.strip()) < 100:
                # Too short, use original content as summary
                source['summary'] = content[:max_length] if content else "No content available"
                source['summarized'] = False
            else:
                summary = self.summarize(content, max_length, min_length)
                
                if summary:
                    source['summary'] = summary
                    source['summarized'] = True
                    console.print(f"[green]✓ {i}/{len(sources)}: Summarized ({len(content)} → {len(summary)} chars)[/green]")
                else:
                    # Fallback to truncated content
                    source['summary'] = content[:max_length] + "..."
                    source['summarized'] = False
                    console.print(f"[yellow]⚠️  {i}/{len(sources)}: Fallback to truncation[/yellow]")
            
            summarized.append(source)
        
        summarized_count = sum(1 for s in summarized if s.get('summarized', False))
        console.print(f"[green]✓ AI Summarization complete: {summarized_count}/{len(sources)} sources summarized[/green]")
        
        return summarized


def research(topic: str, **kwargs) -> Dict:
    """
    OpenClaw-compatible agent interface.
    
    Args:
        topic: Not used (summarization is post-processing)
        sources: List of sources to summarize (required)
        max_length: Maximum summary length (default: 150)
        min_length: Minimum summary length (default: 50)
        model_name: Hugging Face model to use (default: facebook/bart-large-cnn)
    
    Returns:
        Dict with summarized sources
    """
    sources = kwargs.get('sources', [])
    max_length = kwargs.get('max_length', 150)
    min_length = kwargs.get('min_length', 50)
    model_name = kwargs.get('model_name', 'facebook/bart-large-cnn')
    
    if not sources:
        return {
            'success': False,
            'error': 'No sources provided for summarization',
            'sources': []
        }
    
    try:
        summarizer = AISummarizer(model_name=model_name)
        summarized_sources = summarizer.summarize_batch(
            sources,
            max_length=max_length,
            min_length=min_length
        )
        
        return {
            'success': True,
            'sources': summarized_sources,
            'model': model_name,
            'total_sources': len(summarized_sources),
            'summarized_count': sum(1 for s in summarized_sources if s.get('summarized', False))
        }
        
    except Exception as e:
        console.print(f"[red]❌ AI Summarization agent failed: {e}[/red]")
        return {
            'success': False,
            'error': str(e),
            'sources': sources  # Return original sources on failure
        }


if __name__ == "__main__":
    # Test the summarizer
    console.print("[bold cyan]AI Summarization Agent - Test Mode[/bold cyan]")
    
    test_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, 
    in contrast to the natural intelligence displayed by humans and animals. 
    Leading AI textbooks define the field as the study of "intelligent agents": 
    any device that perceives its environment and takes actions that maximize 
    its chance of successfully achieving its goals. Colloquially, the term 
    "artificial intelligence" is often used to describe machines (or computers) 
    that mimic "cognitive" functions that humans associate with the human mind, 
    such as "learning" and "problem solving". As machines become increasingly 
    capable, tasks considered to require "intelligence" are often removed from 
    the definition of AI, a phenomenon known as the AI effect. A quip in 
    Tesler's Theorem says "AI is whatever hasn't been done yet."
    """
    
    summarizer = AISummarizer()
    summary = summarizer.summarize(test_text, max_length=50, min_length=20)
    
    console.print("\n[bold]Original:[/bold]")
    console.print(test_text.strip())
    
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"[green]{summary}[/green]")
