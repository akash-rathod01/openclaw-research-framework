"""
Reasoning Agent - Intelligent Decision Making
Part of OpenClaw Multi-Agent Framework v1.1

This agent makes intelligent decisions about scraping and processing using
rule-based reasoning (zero LLM API costs).

Decisions include:
- Should this URL be scraped?
- Is this content high quality?
- Should we continue deeper?
- Is summarization worth the time?

Author: Akash Rathod
License: MIT
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from urllib.parse import urlparse


class Decision(Enum):
    """Possible decisions the agent can make"""
    PROCEED = "proceed"
    SKIP = "skip"
    RETRY = "retry"
    STOP = "stop"
    OPTIMIZE = "optimize"


@dataclass
class ReasoningContext:
    """Context information for making decisions"""
    url: str = ""
    content_length: int = 0
    content_type: str = ""
    status_code: int = 200
    response_time: float = 0.0
    depth: int = 0
    domain: str = ""
    previous_failures: int = 0
    quality_scores: List[float] = None
    time_budget_remaining: float = 3600.0
    sources_collected: int = 0
    target_sources: int = 50
    
    def __post_init__(self):
        if self.quality_scores is None:
            self.quality_scores = []


@dataclass
class ReasoningResult:
    """Result of a reasoning decision"""
    decision: Decision
    confidence: float  # 0.0 to 1.0
    reasoning: str
    recommendations: List[str]


class ReasoningAgent:
    """
    Rule-based reasoning agent that makes intelligent decisions
    without requiring LLM API calls (stays FREE!).
    """
    
    # Content type preferences
    PREFERRED_CONTENT_TYPES = [
        'text/html',
        'text/plain',
        'application/json',
        'application/xml',
    ]
    
    # File extensions to skip
    SKIP_EXTENSIONS = [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.zip', '.tar', '.gz', '.rar', '.7z',
        '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
        '.mp3', '.mp4', '.avi', '.mov', '.wmv',
        '.exe', '.dmg', '.app', '.deb', '.rpm'
    ]
    
    # Minimum content quality thresholds
    MIN_CONTENT_LENGTH = 500  # bytes
    MAX_CONTENT_LENGTH = 10_000_000  # 10 MB
    ACCEPTABLE_STATUS_CODES = [200, 201, 202, 203, 204]
    MAX_RESPONSE_TIME = 30.0  # seconds
    
    def __init__(self, config: Dict = None):
        """
        Initialize the reasoning agent.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.strict_mode = self.config.get('strict_mode', False)
        self.decisions_made = 0
        self.decision_log: List[str] = []
        
    def should_scrape_url(self, context: ReasoningContext) -> ReasoningResult:
        """
        Decide whether a URL should be scraped.
        
        Args:
            context: ReasoningContext with URL information
            
        Returns:
            ReasoningResult with decision and reasoning
        """
        reasoning_steps = []
        confidence = 1.0
        decision = Decision.PROCEED
        recommendations = []
        
        # Check 1: File extension
        if any(context.url.lower().endswith(ext) for ext in self.SKIP_EXTENSIONS):
            decision = Decision.SKIP
            confidence = 0.95
            reasoning_steps.append("URL points to non-scrapable file type")
            recommendations.append("Skip binary/media files")
            return self._make_result(decision, confidence, reasoning_steps, recommendations)
        
        # Check 2: URL depth
        if context.depth > 5:
            decision = Decision.SKIP
            confidence = 0.8
            reasoning_steps.append(f"URL depth ({context.depth}) exceeds reasonable limit")
            recommendations.append("Focus on shallower, more authoritative pages")
            return self._make_result(decision, confidence, reasoning_steps, recommendations)
        
        # Check 3: Domain blacklist patterns
        blacklist_patterns = [
            r'ads?\.', r'analytics', r'tracking', r'telemetry',
            r'cdn\.', r'static\.', r'assets\.',
        ]
        parsed = urlparse(context.url)
        if any(re.search(pattern, parsed.netloc, re.IGNORECASE) for pattern in blacklist_patterns):
            decision = Decision.SKIP
            confidence = 0.85
            reasoning_steps.append("Domain matches blacklist pattern (ads/tracking/CDN)")
            recommendations.append("Avoid non-content domains")
            return self._make_result(decision, confidence, reasoning_steps, recommendations)
        
        # Check 4: Suspicious URL patterns
        suspicious_patterns = [
            r'/login', r'/signup', r'/register', r'/logout',
            r'/cart', r'/checkout', r'/payment',
            r'/unsubscribe', r'/subscribe',
            r'\?.*(?:session|token|key)=',  # URLs with session tokens
        ]
        if any(re.search(pattern, context.url, re.IGNORECASE) for pattern in suspicious_patterns):
            decision = Decision.SKIP
            confidence = 0.75
            reasoning_steps.append("URL contains suspicious patterns (auth/commerce)")
            recommendations.append("Skip functional/interactive pages")
            return self._make_result(decision, confidence, reasoning_steps, recommendations)
        
        # Check 5: Progress vs target
        if context.sources_collected >= context.target_sources:
            decision = Decision.STOP
            confidence = 1.0
            reasoning_steps.append(f"Target reached: {context.sources_collected}/{context.target_sources}")
            recommendations.append("Goal achieved, safe to stop")
            return self._make_result(decision, confidence, reasoning_steps, recommendations)
        
        # Positive indicators
        reasoning_steps.append("URL passed all quality checks")
        confidence = 0.9
        
        # Boost confidence for valuable patterns
        valuable_patterns = [r'/docs?/', r'/api/', r'/reference/', r'/guide/', r'/tutorial/']
        if any(re.search(pattern, context.url, re.IGNORECASE) for pattern in valuable_patterns):
            confidence = 0.95
            reasoning_steps.append("URL contains valuable content indicators")
            recommendations.append("High-value documentation URL")
        
        return self._make_result(decision, confidence, reasoning_steps, recommendations)
    
    def should_summarize_content(self, context: ReasoningContext) -> ReasoningResult:
        """
        Decide whether content should be summarized.
        
        Args:
            context: ReasoningContext with content information
            
        Returns:
            ReasoningResult with decision and reasoning
        """
        reasoning_steps = []
        confidence = 1.0
        decision = Decision.PROCEED
        recommendations = []
        
        # Check 1: Content length
        if context.content_length < self.MIN_CONTENT_LENGTH:
            decision = Decision.SKIP
            confidence = 0.9
            reasoning_steps.append(f"Content too short ({context.content_length} bytes)")
            recommendations.append("Not worth summarizing short content")
            return self._make_result(decision, confidence, reasoning_steps, recommendations)
        
        if context.content_length > self.MAX_CONTENT_LENGTH:
            decision = Decision.SKIP
            confidence = 0.85
            reasoning_steps.append(f"Content too large ({context.content_length} bytes)")
            recommendations.append("Large content may cause processing issues")
            return self._make_result(decision, confidence, reasoning_steps, recommendations)
        
        # Check 2: Content type
        if context.content_type and not any(
            ct in context.content_type for ct in self.PREFERRED_CONTENT_TYPES
        ):
            decision = Decision.SKIP
            confidence = 0.8
            reasoning_steps.append(f"Unsupported content type: {context.content_type}")
            recommendations.append("Only summarize text-based content")
            return self._make_result(decision, confidence, reasoning_steps, recommendations)
        
        # Check 3: Time budget
        if context.time_budget_remaining < 60:  # Less than 1 minute left
            decision = Decision.SKIP
            confidence = 0.9
            reasoning_steps.append("Time budget nearly exhausted")
            recommendations.append("Prioritize faster operations")
            return self._make_result(decision, confidence, reasoning_steps, recommendations)
        
        # Check 4: Previous quality
        if context.quality_scores:
            avg_quality = sum(context.quality_scores) / len(context.quality_scores)
            if avg_quality < 0.5:
                decision = Decision.OPTIMIZE
                confidence = 0.7
                reasoning_steps.append(f"Low average quality ({avg_quality:.2f})")
                recommendations.append("Consider adjusting summarization parameters")
                return self._make_result(decision, confidence, reasoning_steps, recommendations)
        
        # All checks passed
        reasoning_steps.append("Content suitable for summarization")
        confidence = 0.85
        recommendations.append("Proceed with standard summarization")
        
        return self._make_result(decision, confidence, reasoning_steps, recommendations)
    
    def should_continue_deeper(self, context: ReasoningContext) -> ReasoningResult:
        """
        Decide whether to continue scraping at greater depth.
        
        Args:
            context: ReasoningContext with current state
            
        Returns:
            ReasoningResult with decision and reasoning
        """
        reasoning_steps = []
        confidence = 1.0
        decision = Decision.PROCEED
        recommendations = []
        
        # Check 1: Max depth reached
        if context.depth >= 5:
            decision = Decision.STOP
            confidence = 0.95
            reasoning_steps.append(f"Max reasonable depth reached ({context.depth})")
            recommendations.append("Deeper pages often have diminishing returns")
            return self._make_result(decision, confidence, reasoning_steps, recommendations)
        
        # Check 2: High failure rate
        if context.previous_failures > 5:
            decision = Decision.STOP
            confidence = 0.85
            reasoning_steps.append(f"High failure count: {context.previous_failures}")
            recommendations.append("Stop to avoid wasting resources on failing site")
            return self._make_result(decision, confidence, reasoning_steps, recommendations)
        
        # Check 3: Progress vs target
        progress_ratio = context.sources_collected / max(1, context.target_sources)
        if progress_ratio >= 1.0:
            decision = Decision.STOP
            confidence = 1.0
            reasoning_steps.append("Target sources collected")
            recommendations.append("Goal achieved")
            return self._make_result(decision, confidence, reasoning_steps, recommendations)
        
        if progress_ratio >= 0.8:
            decision = Decision.OPTIMIZE
            confidence = 0.7
            reasoning_steps.append(f"Near target ({progress_ratio:.0%})")
            recommendations.append("Focus on quality over quantity now")
            return self._make_result(decision, confidence, reasoning_steps, recommendations)
        
        # Check 4: Time budget
        time_per_source = context.time_budget_remaining / max(1, context.target_sources - context.sources_collected)
        if time_per_source < 10:  # Less than 10 seconds per remaining source
            decision = Decision.OPTIMIZE
            confidence = 0.75
            reasoning_steps.append("Time budget tight, optimize for efficiency")
            recommendations.append("Skip deep crawling, focus on quick wins")
            return self._make_result(decision, confidence, reasoning_steps, recommendations)
        
        # Continue deeper
        reasoning_steps.append("Conditions favorable for deeper crawling")
        confidence = 0.8
        recommendations.append("Continue to next depth level")
        
        return self._make_result(decision, confidence, reasoning_steps, recommendations)
    
    def assess_content_quality(self, context: ReasoningContext, content: str = "") -> Tuple[float, str]:
        """
        Assess the quality of scraped content.
        
        Args:
            context: ReasoningContext
            content: The actual content string (optional)
            
        Returns:
            Tuple of (quality_score, reasoning)
        """
        quality_score = 0.5  # Start neutral
        reasons = []
        
        # Factor 1: Content length (20% weight)
        if context.content_length > 10000:
            quality_score += 0.1
            reasons.append("Substantial content length")
        elif context.content_length < 1000:
            quality_score -= 0.1
            reasons.append("Short content")
        
        # Factor 2: Response characteristics (20% weight)
        if context.status_code in self.ACCEPTABLE_STATUS_CODES:
            quality_score += 0.1
        else:
            quality_score -= 0.2
            reasons.append(f"Non-200 status: {context.status_code}")
        
        if context.response_time < 2.0:
            quality_score += 0.05
        elif context.response_time > 10.0:
            quality_score -= 0.05
            reasons.append("Slow response time")
        
        # Factor 3: Domain authority (30% weight)
        high_authority = ['.edu', '.gov', '.org', 'github.com', 'stackoverflow.com']
        if any(auth in context.domain for auth in high_authority):
            quality_score += 0.15
            reasons.append("High-authority domain")
        
        # Factor 4: Content analysis if available (30% weight)
        if content:
            # Simple heuristics
            word_count = len(content.split())
            if word_count > 300:
                quality_score += 0.1
                reasons.append(f"Good word count: {word_count}")
            
            # Check for code snippets (valuable for technical content)
            if '<code>' in content or '```' in content or '<pre>' in content:
                quality_score += 0.1
                reasons.append("Contains code examples")
            
            # Check for structured content
            if any(tag in content for tag in ['<h1>', '<h2>', '<h3>', '<ul>', '<ol>']):
                quality_score += 0.05
                reasons.append("Well-structured content")
        
        # Normalize to 0-1 range
        quality_score = max(0.0, min(1.0, quality_score))
        
        reasoning = "; ".join(reasons) if reasons else "Standard content quality"
        
        return quality_score, reasoning
    
    def _make_result(
        self,
        decision: Decision,
        confidence: float,
        reasoning_steps: List[str],
        recommendations: List[str]
    ) -> ReasoningResult:
        """Create a ReasoningResult object."""
        self.decisions_made += 1
        reasoning = " | ".join(reasoning_steps)
        
        # Log decision
        log_entry = f"Decision #{self.decisions_made}: {decision.value} (confidence: {confidence:.2f})"
        self.decision_log.append(log_entry)
        
        return ReasoningResult(
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            recommendations=recommendations
        )
    
    def get_decision_report(self) -> str:
        """Generate a report of all decisions made."""
        report = "\n" + "="*80 + "\n"
        report += "REASONING AGENT DECISION REPORT\n"
        report += "="*80 + "\n\n"
        
        report += f"Total Decisions Made: {self.decisions_made}\n"
        report += f"Mode: {'Strict' if self.strict_mode else 'Normal'}\n\n"
        
        report += "Recent Decisions:\n"
        for entry in self.decision_log[-20:]:  # Last 20 decisions
            report += f"  {entry}\n"
        
        report += "\n" + "="*80 + "\n"
        
        return report


# Example usage
if __name__ == "__main__":
    agent = ReasoningAgent()
    
    # Test URL scraping decision
    context1 = ReasoningContext(
        url="https://docs.python.org/3/library/",
        depth=2,
        domain="docs.python.org",
        sources_collected=15,
        target_sources=50
    )
    
    result1 = agent.should_scrape_url(context1)
    print(f"Decision: {result1.decision.value}")
    print(f"Confidence: {result1.confidence:.2f}")
    print(f"Reasoning: {result1.reasoning}")
    print(f"Recommendations: {', '.join(result1.recommendations)}")
    print()
    
    # Test summarization decision
    context2 = ReasoningContext(
        content_length=5000,
        content_type="text/html",
        time_budget_remaining=1800,
        quality_scores=[0.75, 0.82, 0.79]
    )
    
    result2 = agent.should_summarize_content(context2)
    print(f"Decision: {result2.decision.value}")
    print(f"Confidence: {result2.confidence:.2f}")
    print(f"Reasoning: {result2.reasoning}")
    print()
    
    # Print decision report
    print(agent.get_decision_report())
