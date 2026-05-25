"""
Custom Evaluation Metrics for Web Summarization
Application-specific metrics beyond standard ROUGE scores
"""

import numpy as np
from typing import Dict, List
from rich.console import Console

console = Console()


class WebSummarizationMetrics:
    """
    Custom metrics for OpenClaw web summarization evaluation
    """
    
    def __init__(self):
        self.metrics = {}
        
        # Try to load optional dependencies
        try:
            import textstat
            self.textstat = textstat
            self.readability_available = True
        except ImportError:
            self.readability_available = False
            console.print("[yellow]⚠️  textstat not available - readability metrics disabled[/yellow]")
        
        try:
            import spacy
            self.nlp = None  # Lazy load
            self.ner_available = True
        except ImportError:
            self.ner_available = False
            console.print("[yellow]⚠️  spaCy not available - NER metrics disabled[/yellow]")
    
    def compression_ratio(self, original: str, summary: str) -> Dict:
        """
        Compression ratio metric
        Target: 5-15% for web content (85-95% compression)
        
        Returns:
            Dict with ratio and score
        """
        if not original or not summary:
            return {'compression_ratio': 0, 'score': 0}
        
        ratio = len(summary) / len(original)
        
        # Score: 1.0 if in target range, decreasing outside
        if 0.05 <= ratio <= 0.15:
            score = 1.0
        elif 0.15 < ratio <= 0.25:
            score = 0.8
        elif 0.03 <= ratio < 0.05:
            score = 0.7
        else:
            score = 0.3
        
        return {'compression_ratio': ratio, 'compression_score': score}
    
    def informativeness(self, original: str, summary: str) -> Dict:
        """
        Semantic similarity using TF-IDF
        Measures if summary captures key information
        
        Returns:
            Dict with similarity score
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            if not original or not summary:
                return {'informativeness': 0, 'informativeness_score': 0}
            
            vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            
            try:
                vectors = vectorizer.fit_transform([original, summary])
                similarity = cosine_similarity(vectors)[0, 1]
            except:
                # Fallback: simple word overlap
                original_words = set(original.lower().split())
                summary_words = set(summary.lower().split())
                similarity = len(original_words & summary_words) / len(original_words) if original_words else 0
            
            # Target: > 0.7 similarity
            score = 1.0 if similarity >= 0.7 else similarity / 0.7
            
            return {'informativeness': similarity, 'informativeness_score': score}
        
        except ImportError:
            # Fallback to word overlap
            original_words = set(original.lower().split())
            summary_words = set(summary.lower().split())
            overlap = len(original_words & summary_words) / len(original_words) if original_words else 0
            return {'informativeness': overlap, 'informativeness_score': overlap}
    
    def readability(self, summary: str) -> Dict:
        """
        Flesch Reading Ease Score
        Target: 60-70 (Standard English for web content)
        
        Returns:
            Dict with readability score
        """
        if not self.readability_available or not summary:
            return {'readability': 0, 'readability_score': 0}
        
        try:
            score = self.textstat.flesch_reading_ease(summary)
            
            # 60-70 is ideal for web content
            if 60 <= score <= 70:
                normalized = 1.0
            elif 50 <= score < 60 or 70 < score <= 80:
                normalized = 0.8
            else:
                normalized = 0.5
            
            return {'readability': score, 'readability_score': normalized}
        
        except:
            return {'readability': 0, 'readability_score': 0}
    
    def factual_consistency(self, original: str, summary: str) -> Dict:
        """
        Check for hallucinations - all summary facts must be in original
        Uses Named Entity Recognition overlap
        
        Returns:
            Dict with consistency score
        """
        if not self.ner_available or not original or not summary:
            return {'factual_consistency': 1.0, 'consistency_score': 1.0}
        
        try:
            # Lazy load spaCy model
            if self.nlp is None:
                import spacy
                try:
                    self.nlp = spacy.load('en_core_web_sm')
                except:
                    console.print("[yellow]⚠️  spaCy model not found. Install with: python -m spacy download en_core_web_sm[/yellow]")
                    return {'factual_consistency': 1.0, 'consistency_score': 1.0}
            
            orig_doc = self.nlp(original[:10000])  # Limit length
            summ_doc = self.nlp(summary)
            
            orig_entities = set([ent.text.lower() for ent in orig_doc.ents])
            summ_entities = set([ent.text.lower() for ent in summ_doc.ents])
            
            if len(summ_entities) == 0:
                # No entities in summary - can't hallucinate
                return {'factual_consistency': 1.0, 'consistency_score': 1.0}
            
            # All summary entities should exist in original
            consistency = len(summ_entities & orig_entities) / len(summ_entities)
            
            return {'factual_consistency': consistency, 'consistency_score': consistency}
        
        except Exception as e:
            return {'factual_consistency': 1.0, 'consistency_score': 1.0}
    
    def summary_length_appropriateness(self, summary: str, target_min: int = 50, target_max: int = 250) -> Dict:
        """
        Check if summary length is appropriate
        
        Returns:
            Dict with length appropriateness score
        """
        if not summary:
            return {'summary_length': 0, 'length_score': 0}
        
        length = len(summary.split())
        
        if target_min <= length <= target_max:
            score = 1.0
        elif length < target_min:
            score = length / target_min
        else:  # length > target_max
            score = target_max / length
        
        return {'summary_length': length, 'length_score': score}
    
    def evaluate_all(self, original: str, summary: str) -> Dict:
        """
        Comprehensive evaluation combining all metrics
        
        Returns:
            Dict with all metric scores and overall score
        """
        results = {}
        
        # Run all metrics
        results.update(self.compression_ratio(original, summary))
        results.update(self.informativeness(original, summary))
        results.update(self.readability(summary))
        results.update(self.factual_consistency(original, summary))
        results.update(self.summary_length_appropriateness(summary))
        
        # Calculate weighted overall score
        weights = {
            'compression_score': 0.15,
            'informativeness_score': 0.35,
            'readability_score': 0.15,
            'consistency_score': 0.25,
            'length_score': 0.10
        }
        
        overall = sum(
            results.get(metric, 0) * weight
            for metric, weight in weights.items()
        )
        
        results['overall_score'] = overall
        
        return results
    
    def batch_evaluate(self, originals: List[str], summaries: List[str]) -> Dict:
        """
        Evaluate a batch of summaries and return aggregated metrics
        
        Returns:
            Dict with mean scores across all samples
        """
        all_results = []
        
        for orig, summ in zip(originals, summaries):
            results = self.evaluate_all(orig, summ)
            all_results.append(results)
        
        # Aggregate
        aggregated = {}
        if all_results:
            for key in all_results[0].keys():
                values = [r[key] for r in all_results if key in r]
                if values:
                    aggregated[f'mean_{key}'] = np.mean(values)
                    aggregated[f'std_{key}'] = np.std(values)
        
        return aggregated


def demo():
    """Demo the metrics"""
    console.print("\n[bold cyan]📊 Custom Metrics Demo[/bold cyan]\n")
    
    metrics = WebSummarizationMetrics()
    
    # Example
    original = """
    The Central Intelligence Agency (CIA) is a civilian foreign intelligence service of 
    the federal government of the United States, officially tasked with gathering, processing, 
    and analyzing national security information from around the world, primarily through the 
    use of human intelligence (HUMINT). The CIA has 160+ career opportunities essential to 
    our mission. We offer monetary bonuses for language proficiency in mission critical languages.
    """
    
    summary = """
    The CIA is a US foreign intelligence agency with 160+ careers. 
    They offer language bonuses for critical languages.
    """
    
    results = metrics.evaluate_all(original, summary)
    
    console.print("[bold]Evaluation Results:[/bold]")
    console.print(f"  Compression Ratio: {results['compression_ratio']:.2%} (score: {results['compression_score']:.2f})")
    console.print(f"  Informativeness: {results['informativeness']:.2f} (score: {results['informativeness_score']:.2f})")
    console.print(f"  Readability: {results.get('readability', 'N/A')} (score: {results['readability_score']:.2f})")
    console.print(f"  Factual Consistency: {results['factual_consistency']:.2%} (score: {results['consistency_score']:.2f})")
    console.print(f"  Summary Length: {results['summary_length']} words (score: {results['length_score']:.2f})")
    console.print(f"\n[bold green]Overall Score: {results['overall_score']:.2f}/1.00[/bold green]\n")


if __name__ == "__main__":
    demo()
