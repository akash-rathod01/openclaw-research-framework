"""
Source Ranking Agent - Intelligent URL Prioritization
Part of OpenClaw Multi-Agent Framework v1.1

This agent analyzes and ranks URLs based on multiple factors:
- Domain authority (educational, government, trusted domains)
- URL structure and depth
- Content type indicators
- Relevance to research goals

Author: Akash Rathod
License: MIT
"""

import re
from urllib.parse import urlparse
from typing import List, Dict, Tuple
from dataclasses import dataclass, field


@dataclass
class URLScore:
    """Represents a scored URL with breakdown of score components"""
    url: str
    total_score: float = 0.0
    domain_score: float = 0.0
    structure_score: float = 0.0
    content_score: float = 0.0
    depth_penalty: float = 0.0
    reasoning: str = ""


class SourceRanker:
    """
    Intelligent source ranking system that prioritizes URLs based on multiple factors.
    Uses rule-based scoring to maintain zero-cost operation.
    """
    
    # Domain authority weights
    HIGH_AUTHORITY_DOMAINS = {
        '.edu': 1.0,      # Educational institutions
        '.gov': 1.0,      # Government sites
        '.org': 0.8,      # Organizations
        'github.com': 0.9,
        'stackoverflow.com': 0.85,
        'wikipedia.org': 0.85,
        'arxiv.org': 0.95,
        'nature.com': 0.9,
        'science.org': 0.9,
        'ieee.org': 0.9,
    }
    
    # Content type indicators
    VALUABLE_KEYWORDS = [
        'research', 'paper', 'publication', 'journal', 'article',
        'documentation', 'tutorial', 'guide', 'reference', 'api',
        'study', 'analysis', 'report', 'whitepaper', 'technical'
    ]
    
    # Low-value indicators
    LOW_VALUE_PATTERNS = [
        r'/tag/', r'/category/', r'/author/', r'/page/',
        r'/login', r'/signup', r'/register', r'/cart',
        r'/privacy', r'/terms', r'/cookie', r'/legal',
        r'\d{4}/\d{2}/\d{2}',  # Date patterns (often blog posts)
    ]
    
    def __init__(self, config: Dict = None):
        """
        Initialize the source ranker.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.max_depth = self.config.get('max_depth', 5)
        self.prioritize_depth = self.config.get('prioritize_depth', 'shallow')  # 'shallow' or 'deep'
        
    def rank_sources(self, urls: List[str], context: str = "") -> List[URLScore]:
        """
        Rank a list of URLs by importance and relevance.
        
        Args:
            urls: List of URLs to rank
            context: Optional context string to help with relevance scoring
            
        Returns:
            List of URLScore objects sorted by total_score (highest first)
        """
        scored_urls = []
        
        for url in urls:
            score = self._score_url(url, context)
            scored_urls.append(score)
        
        # Sort by total score (descending)
        scored_urls.sort(key=lambda x: x.total_score, reverse=True)
        
        return scored_urls
    
    def get_priority_urls(self, urls: List[str], top_n: int = None, context: str = "") -> List[str]:
        """
        Get the top N priority URLs from a list.
        
        Args:
            urls: List of URLs to rank
            top_n: Number of top URLs to return (None = return all)
            context: Optional context for relevance scoring
            
        Returns:
            List of URLs sorted by priority
        """
        ranked = self.rank_sources(urls, context)
        
        if top_n:
            ranked = ranked[:top_n]
        
        return [score.url for score in ranked]
    
    def _score_url(self, url: str, context: str = "") -> URLScore:
        """
        Calculate comprehensive score for a single URL.
        
        Args:
            url: URL to score
            context: Context for relevance
            
        Returns:
            URLScore object with detailed scoring
        """
        score = URLScore(url=url)
        
        # Parse URL
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            # 1. Domain Authority Score (0-1)
            score.domain_score = self._calculate_domain_score(domain)
            
            # 2. URL Structure Score (0-1)
            score.structure_score = self._calculate_structure_score(path, parsed.query)
            
            # 3. Content Relevance Score (0-1)
            score.content_score = self._calculate_content_score(url, context)
            
            # 4. Depth Penalty (0 to -0.5)
            score.depth_penalty = self._calculate_depth_penalty(path)
            
            # Calculate total score (weighted average)
            score.total_score = (
                score.domain_score * 0.35 +
                score.structure_score * 0.25 +
                score.content_score * 0.25 +
                (1.0 + score.depth_penalty) * 0.15
            )
            
            # Generate reasoning
            score.reasoning = self._generate_reasoning(score)
            
        except Exception as e:
            score.total_score = 0.3  # Default low score for problematic URLs
            score.reasoning = f"Parsing error: {str(e)}"
        
        return score
    
    def _calculate_domain_score(self, domain: str) -> float:
        """Calculate score based on domain authority."""
        score = 0.5  # Default neutral score
        
        # Check for high-authority domains
        for authority_domain, authority_score in self.HIGH_AUTHORITY_DOMAINS.items():
            if authority_domain in domain:
                score = authority_score
                break
        
        # Boost for HTTPS (implied by modern practices)
        # Additional heuristics could be added here
        
        return score
    
    def _calculate_structure_score(self, path: str, query: str) -> float:
        """Calculate score based on URL structure quality."""
        score = 0.7  # Default decent score
        
        # Penalize low-value patterns
        for pattern in self.LOW_VALUE_PATTERNS:
            if re.search(pattern, path):
                score -= 0.2
                break
        
        # Penalize complex query strings (often dynamic/low-value pages)
        if query and len(query) > 50:
            score -= 0.1
        
        # Penalize overly long paths
        path_segments = [p for p in path.split('/') if p]
        if len(path_segments) > 6:
            score -= 0.1
        
        # Boost for clean, documentation-style URLs
        if re.search(r'/docs?/', path) or re.search(r'/guide/', path):
            score += 0.2
        
        return max(0.0, min(1.0, score))
    
    def _calculate_content_score(self, url: str, context: str) -> float:
        """Calculate score based on content indicators."""
        score = 0.5  # Neutral default
        
        url_lower = url.lower()
        
        # Check for valuable keywords in URL
        keyword_count = sum(1 for keyword in self.VALUABLE_KEYWORDS if keyword in url_lower)
        score += min(keyword_count * 0.1, 0.3)  # Up to +0.3 for keywords
        
        # Context relevance (if context provided)
        if context:
            context_lower = context.lower()
            context_words = set(context_lower.split())
            url_words = set(re.findall(r'\w+', url_lower))
            
            # Calculate word overlap
            overlap = len(context_words & url_words)
            if overlap > 0:
                score += min(overlap * 0.05, 0.2)  # Up to +0.2 for context match
        
        return min(1.0, score)
    
    def _calculate_depth_penalty(self, path: str) -> float:
        """Calculate penalty based on URL depth."""
        path_segments = [p for p in path.split('/') if p]
        depth = len(path_segments)
        
        if self.prioritize_depth == 'shallow':
            # Prefer shallower pages (likely overview/main content)
            if depth <= 2:
                return 0.0
            elif depth <= 4:
                return -0.1
            else:
                return -0.3
        else:
            # Prefer deeper pages (detailed content)
            if depth >= 4:
                return 0.0
            elif depth >= 2:
                return -0.1
            else:
                return -0.2
        
        return 0.0
    
    def _generate_reasoning(self, score: URLScore) -> str:
        """Generate human-readable reasoning for the score."""
        reasons = []
        
        if score.domain_score >= 0.8:
            reasons.append("High-authority domain")
        elif score.domain_score >= 0.6:
            reasons.append("Trusted domain")
        else:
            reasons.append("Standard domain")
        
        if score.structure_score >= 0.8:
            reasons.append("clean URL structure")
        elif score.structure_score < 0.5:
            reasons.append("complex/low-value URL pattern")
        
        if score.content_score >= 0.7:
            reasons.append("relevant content indicators")
        
        if score.depth_penalty < -0.2:
            reasons.append("deep nesting penalty")
        
        return "; ".join(reasons)
    
    def get_ranking_report(self, urls: List[str], context: str = "", top_n: int = 10) -> str:
        """
        Generate a formatted report of URL rankings.
        
        Args:
            urls: List of URLs to rank
            context: Optional context
            top_n: Number of top URLs to show
            
        Returns:
            Formatted string report
        """
        ranked = self.rank_sources(urls, context)[:top_n]
        
        report = f"\n{'='*80}\n"
        report += f"SOURCE RANKING REPORT - Top {top_n} URLs\n"
        report += f"{'='*80}\n\n"
        
        for idx, score in enumerate(ranked, 1):
            report += f"{idx}. Score: {score.total_score:.3f}\n"
            report += f"   URL: {score.url}\n"
            report += f"   Breakdown: Domain={score.domain_score:.2f}, "
            report += f"Structure={score.structure_score:.2f}, "
            report += f"Content={score.content_score:.2f}, "
            report += f"Depth={score.depth_penalty:.2f}\n"
            report += f"   Reasoning: {score.reasoning}\n\n"
        
        return report


# Example usage and testing
if __name__ == "__main__":
    ranker = SourceRanker()
    
    test_urls = [
        "https://www.iitb.ac.in/en/education/courses",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://github.com/features/copilot",
        "https://docs.python.org/3/library/",
        "https://stackoverflow.com/questions/tagged/python",
        "https://example.com/blog/2024/01/15/random-post",
        "https://example.com/category/news/",
        "https://arxiv.org/abs/2401.12345",
        "https://www.nature.com/articles/nature12345",
    ]
    
    print(ranker.get_ranking_report(test_urls, context="machine learning python", top_n=5))
