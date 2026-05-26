"""
Evaluator Agent - Post-Processing Quality Assurance
Part of OpenClaw Multi-Agent Framework v1.2

This agent evaluates scraped content and summaries for:
- Output quality scoring
- Consistency checking  
- Hallucination detection
- Retry triggering

Author: Akash Rathod
License: MIT
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import difflib
from datetime import datetime


class ValidationStatus(Enum):
    """Validation status for evaluated content"""
    PASS = "PASS"
    FAIL = "FAIL"
    RETRY = "RETRY"
    NEEDS_VALIDATION = "NEEDS_VALIDATION"


class HallucinationType(Enum):
    """Types of hallucination detected"""
    FACTUAL_ERROR = "factual_error"
    UNSUPPORTED_CLAIM = "unsupported_claim"
    LOGICAL_INCONSISTENCY = "logical_inconsistency"
    CONTRADICTORY_STATEMENT = "contradictory_statement"
    FABRICATED_DATA = "fabricated_data"


@dataclass
class EvaluationResult:
    """Complete evaluation result with all metrics"""
    
    # Main output
    answer: str
    confidence: float  # 0.0 - 1.0
    source_quality: float  # 0.0 - 1.0
    validation_status: ValidationStatus
    
    # Detailed scores
    hallucination_score: float  # 0.0 (none) - 1.0 (severe)
    consistency_score: float  # 0.0 - 1.0
    factual_accuracy: float  # 0.0 - 1.0
    content_quality: float  # 0.0 - 1.0
    summary_quality: float  # 0.0 - 1.0
    information_density: float  # 0.0 - 1.0
    coherence: float  # 0.0 - 1.0
    
    # Metadata
    sources_verified: int
    contradictions_found: int
    retry_count: int
    hallucinations_detected: List[str] = field(default_factory=list)
    
    # Reasoning
    reasoning: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    # Quality breakdown
    quality_breakdown: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HallucinationDetection:
    """Detected hallucination instance"""
    type: HallucinationType
    claim: str
    severity: float  # 0.0 - 1.0
    evidence_against: List[str]
    confidence: float  # How confident we are this is a hallucination
    reasoning: str


class EvaluatorAgent:
    """
    Evaluates output quality, checks consistency, detects hallucination
    """
    
    def __init__(self):
        self.evaluation_history = []
        self.hallucination_patterns = self._load_hallucination_patterns()
        
    def evaluate(
        self,
        original_content: str,
        summary: str,
        sources: List[str],
        metadata: Optional[Dict] = None
    ) -> EvaluationResult:
        """
        Main evaluation entry point
        
        Args:
            original_content: Original scraped content
            summary: AI-generated summary
            sources: Source URLs
            metadata: Additional metadata
            
        Returns:
            Complete evaluation result
        """
        metadata = metadata or {}
        
        # 1. Score output quality
        output_score = self._score_output(summary)
        
        # 2. Check consistency
        consistency_score = self._check_consistency(original_content, summary)
        
        # 3. Detect hallucination
        hallucination_result = self._detect_hallucination(
            original_content, 
            summary
        )
        
        # 4. Calculate source quality
        source_quality = self._calculate_source_quality(sources, metadata)
        
        # 5. Calculate factual accuracy
        factual_accuracy = self._calculate_factual_accuracy(
            original_content,
            summary,
            hallucination_result
        )
        
        # 6. Determine validation status
        validation_status = self._determine_validation_status(
            output_score,
            consistency_score,
            hallucination_result,
            source_quality
        )
        
        # 7. Calculate overall confidence
        confidence = self._calculate_confidence(
            output_score,
            consistency_score,
            hallucination_result.score,
            source_quality,
            factual_accuracy
        )
        
        # 8. Create quality breakdown
        quality_breakdown = {
            "content_quality": metadata.get('content_quality', output_score),
            "summary_quality": output_score,
            "information_density": self._calculate_info_density(summary),
            "coherence": self._calculate_coherence(summary)
        }
        
        # 9. Generate reasoning and recommendations
        reasoning, recommendations = self._generate_reasoning(
            confidence,
            validation_status,
            hallucination_result,
            consistency_score
        )
        
        # 10. Create evaluation result
        result = EvaluationResult(
            answer=summary,
            confidence=confidence,
            source_quality=source_quality,
            validation_status=validation_status,
            hallucination_score=hallucination_result.score,
            consistency_score=consistency_score,
            factual_accuracy=factual_accuracy,
            content_quality=quality_breakdown['content_quality'],
            summary_quality=quality_breakdown['summary_quality'],
            information_density=quality_breakdown['information_density'],
            coherence=quality_breakdown['coherence'],
            sources_verified=len(sources),
            contradictions_found=len(hallucination_result.contradictions),
            retry_count=metadata.get('retry_count', 0),
            hallucinations_detected=hallucination_result.hallucinations,
            reasoning=reasoning,
            recommendations=recommendations,
            quality_breakdown=quality_breakdown,
            metadata={
                'timestamp': datetime.now().isoformat(),
                'evaluation_id': self._generate_eval_id(),
                'sources': sources
            }
        )
        
        self.evaluation_history.append(result)
        return result
    
    def _score_output(self, summary: str) -> float:
        """
        Score the quality of output summary
        
        Criteria:
        - Length appropriateness
        - Completeness
        - Clarity
        - Structure
        """
        score = 0.0
        
        # Length check (50-500 words ideal)
        word_count = len(summary.split())
        if 50 <= word_count <= 500:
            length_score = 1.0
        elif word_count < 50:
            length_score = word_count / 50
        else:
            length_score = max(0.5, 1.0 - ((word_count - 500) / 1000))
        score += length_score * 0.25
        
        # Completeness (has key elements)
        has_subject = bool(re.search(r'\b(the|a|an)\s+\w+', summary, re.I))
        has_verb = bool(re.search(r'\b(is|are|was|were|has|have|do|does)\b', summary, re.I))
        has_object = len(summary.split()) > 5
        completeness_score = sum([has_subject, has_verb, has_object]) / 3
        score += completeness_score * 0.25
        
        # Clarity (no excessive punctuation, proper capitalization)
        clarity_score = 1.0
        if summary.count('!!!') > 0 or summary.count('???') > 0:
            clarity_score -= 0.3
        if not summary[0].isupper():
            clarity_score -= 0.2
        score += max(0, clarity_score) * 0.25
        
        # Structure (sentences, paragraphs)
        sentences = summary.split('.')
        if 2 <= len(sentences) <= 10:
            structure_score = 1.0
        else:
            structure_score = 0.7
        score += structure_score * 0.25
        
        return min(1.0, score)
    
    def _check_consistency(
        self, 
        original: str, 
        summary: str
    ) -> float:
        """
        Check consistency between original and summary
        
        Returns:
            Consistency score 0.0-1.0
        """
        # Extract key phrases from both
        original_phrases = self._extract_key_phrases(original)
        summary_phrases = self._extract_key_phrases(summary)
        
        # Calculate overlap
        if not original_phrases:
            return 0.5  # Unknown
        
        matching = len(set(original_phrases) & set(summary_phrases))
        consistency = matching / len(original_phrases) if original_phrases else 0
        
        # Check for numerical consistency
        original_numbers = self._extract_numbers(original)
        summary_numbers = self._extract_numbers(summary)
        
        numerical_consistency = 1.0
        for num in summary_numbers:
            if num not in original_numbers:
                # Check if it's close (rounding)
                close_match = any(abs(num - orig) / orig < 0.1 for orig in original_numbers if orig > 0)
                if not close_match:
                    numerical_consistency -= 0.2
        
        numerical_consistency = max(0, numerical_consistency)
        
        # Weighted average
        return consistency * 0.6 + numerical_consistency * 0.4
    
    def _detect_hallucination(
        self,
        original: str,
        summary: str
    ) -> 'HallucinationResult':
        """
        Detect hallucinations in summary
        
        Types:
        - Claims not in original
        - Contradictory statements
        - Fabricated numbers
        - Unsupported generalizations
        """
        hallucinations = []
        contradictions = []
        
        # Extract claims from summary
        summary_claims = self._extract_claims(summary)
        original_claims = self._extract_claims(original)
        
        for claim in summary_claims:
            # Check if claim is supported by original
            if not self._is_claim_supported(claim, original_claims):
                hallucinations.append(f"Unsupported claim: {claim}")
        
        # Check for numerical fabrications
        original_numbers = set(self._extract_numbers(original))
        summary_numbers = set(self._extract_numbers(summary))
        
        fabricated_numbers = summary_numbers - original_numbers
        for num in fabricated_numbers:
            # Allow 10% rounding error
            if not any(abs(num - orig) / orig < 0.1 for orig in original_numbers if orig > 0):
                hallucinations.append(f"Fabricated number: {num}")
        
        # Check for contradictions within summary
        contradictions = self._find_internal_contradictions(summary)
        
        # Calculate hallucination score
        hallucination_score = min(1.0, (len(hallucinations) + len(contradictions)) / 10)
        
        return type('HallucinationResult', (), {
            'score': hallucination_score,
            'hallucinations': hallucinations,
            'contradictions': contradictions,
            'severity': 'HIGH' if hallucination_score > 0.5 else 'MEDIUM' if hallucination_score > 0.2 else 'LOW'
        })()
    
    def _calculate_source_quality(
        self,
        sources: List[str],
        metadata: Dict
    ) -> float:
        """Calculate quality score for sources"""
        if not sources:
            return 0.5
        
        quality = 0.0
        
        # Domain authority
        high_authority_domains = ['.edu', '.gov', '.org', 'wikipedia.org', 'github.com']
        authority_score = sum(
            1 for source in sources 
            if any(domain in source for domain in high_authority_domains)
        ) / len(sources)
        quality += authority_score * 0.4
        
        # Source diversity
        unique_domains = len(set(self._extract_domain(s) for s in sources))
        diversity_score = min(1.0, unique_domains / 5)
        quality += diversity_score * 0.3
        
        # Recency (if timestamp available)
        recency_score = metadata.get('recency_score', 0.7)
        quality += recency_score * 0.3
        
        return quality
    
    def _calculate_factual_accuracy(
        self,
        original: str,
        summary: str,
        hallucination_result: Any
    ) -> float:
        """
        Calculate factual accuracy score
        
        Based on:
        - Hallucination score (inverse)
        - Claim verification
        - Numerical accuracy
        """
        # Start with inverse of hallucination score
        accuracy = 1.0 - hallucination_result.score
        
        # Adjust for number of claims
        claims = self._extract_claims(summary)
        if claims:
            verified_claims = sum(
                1 for claim in claims
                if claim.lower() in original.lower()
            )
            claim_accuracy = verified_claims / len(claims)
            accuracy = accuracy * 0.7 + claim_accuracy * 0.3
        
        return accuracy
    
    def _determine_validation_status(
        self,
        output_score: float,
        consistency_score: float,
        hallucination_result: Any,
        source_quality: float
    ) -> ValidationStatus:
        """
        Determine overall validation status
        
        Decision tree:
        - PASS: High scores, no hallucinations
        - RETRY: Low scores, might improve
        - FAIL: Critical issues found
        - NEEDS_VALIDATION: Borderline, needs human review
        """
        # Critical failures
        if hallucination_result.score > 0.7:
            return ValidationStatus.FAIL
        
        if output_score < 0.3 or consistency_score < 0.3:
            return ValidationStatus.RETRY
        
        # Clear pass
        if all([
            output_score >= 0.7,
            consistency_score >= 0.7,
            hallucination_result.score < 0.2,
            source_quality >= 0.6
        ]):
            return ValidationStatus.PASS
        
        # Borderline - needs validation
        if any([
            0.5 <= hallucination_result.score <= 0.7,
            0.4 <= output_score < 0.7,
            0.4 <= consistency_score < 0.7
        ]):
            return ValidationStatus.NEEDS_VALIDATION
        
        # Retry for improvable issues
        return ValidationStatus.RETRY
    
    def _calculate_confidence(
        self,
        output_score: float,
        consistency_score: float,
        hallucination_score: float,
        source_quality: float,
        factual_accuracy: float
    ) -> float:
        """
        Calculate overall confidence score
        
        Weighted combination of all metrics
        """
        confidence = (
            output_score * 0.20 +
            consistency_score * 0.25 +
            (1 - hallucination_score) * 0.25 +
            source_quality * 0.15 +
            factual_accuracy * 0.15
        )
        
        return min(1.0, max(0.0, confidence))
    
    def _generate_reasoning(
        self,
        confidence: float,
        status: ValidationStatus,
        hallucination_result: Any,
        consistency_score: float
    ) -> Tuple[str, List[str]]:
        """Generate human-readable reasoning and recommendations"""
        
        reasoning_parts = []
        recommendations = []
        
        # Confidence assessment
        if confidence >= 0.8:
            reasoning_parts.append("High confidence result.")
        elif confidence >= 0.6:
            reasoning_parts.append("Moderate confidence result.")
        else:
            reasoning_parts.append("Low confidence result.")
        
        # Hallucination assessment
        if hallucination_result.score < 0.2:
            reasoning_parts.append("No significant hallucinations detected.")
        else:
            reasoning_parts.append(f"{len(hallucination_result.hallucinations)} potential hallucinations found.")
            recommendations.append("Review hallucinated claims before using")
        
        # Consistency assessment
        if consistency_score >= 0.7:
            reasoning_parts.append("Summary is consistent with original content.")
        else:
            reasoning_parts.append("Summary has consistency issues with original.")
            recommendations.append("Cross-reference with original source")
        
        # Status-specific reasoning
        if status == ValidationStatus.PASS:
            reasoning_parts.append("Content passed all quality checks.")
        elif status == ValidationStatus.RETRY:
            reasoning_parts.append("Content should be re-scraped for better quality.")
            recommendations.append("Retry scraping with different parameters")
        elif status == ValidationStatus.FAIL:
            reasoning_parts.append("Content failed critical quality checks.")
            recommendations.append("Discard this result and try alternative sources")
        else:  # NEEDS_VALIDATION
            reasoning_parts.append("Content requires human validation.")
            recommendations.append("Manual review recommended before use")
        
        reasoning = " ".join(reasoning_parts)
        return reasoning, recommendations
    
    # Helper methods
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        # Simple implementation - could use NLP library
        words = text.lower().split()
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        phrases = [w for w in words if len(w) > 3 and w not in stop_words]
        return phrases[:20]  # Top 20 key phrases
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numerical values from text"""
        numbers = re.findall(r'\d+\.?\d*', text)
        return [float(n) for n in numbers]
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract factual claims from text"""
        # Split by sentences
        sentences = re.split(r'[.!?]+', text)
        # Filter for claim-like sentences (has subject, verb, object)
        claims = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence.split()) >= 5:  # Minimum length
                claims.append(sentence)
        return claims
    
    def _is_claim_supported(self, claim: str, original_claims: List[str]) -> bool:
        """Check if claim is supported by original claims"""
        claim_lower = claim.lower()
        for original in original_claims:
            similarity = difflib.SequenceMatcher(None, claim_lower, original.lower()).ratio()
            if similarity > 0.6:
                return True
        return False
    
    def _find_internal_contradictions(self, text: str) -> List[str]:
        """Find contradictory statements within text"""
        contradictions = []
        claims = self._extract_claims(text)
        
        for i, claim1 in enumerate(claims):
            for claim2 in claims[i+1:]:
                if self._are_contradictory(claim1, claim2):
                    contradictions.append(f"{claim1} <-> {claim2}")
        
        return contradictions
    
    def _are_contradictory(self, claim1: str, claim2: str) -> bool:
        """Check if two claims contradict each other"""
        # Simple implementation - check for numerical contradictions
        nums1 = self._extract_numbers(claim1)
        nums2 = self._extract_numbers(claim2)
        
        # If same numbers appear with different values
        if nums1 and nums2:
            for n1 in nums1:
                for n2 in nums2:
                    if abs(n1 - n2) > max(n1, n2) * 0.5:  # 50% difference
                        return True
        
        return False
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        match = re.search(r'://([^/]+)', url)
        return match.group(1) if match else url
    
    def _calculate_info_density(self, text: str) -> float:
        """Calculate information density"""
        words = text.split()
        unique_words = len(set(words))
        return min(1.0, unique_words / len(words)) if words else 0
    
    def _calculate_coherence(self, text: str) -> float:
        """Calculate text coherence"""
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) < 2:
            return 1.0
        
        # Check for transition words
        transitions = ['however', 'therefore', 'moreover', 'additionally', 'furthermore']
        has_transitions = sum(1 for s in sentences if any(t in s.lower() for t in transitions))
        
        return min(1.0, has_transitions / len(sentences) + 0.5)
    
    def _load_hallucination_patterns(self) -> List[str]:
        """Load patterns that indicate hallucination"""
        return [
            r'according to (unnamed|anonymous) sources',
            r'it is believed that',
            r'some say that',
            r'rumors suggest',
        ]
    
    def _generate_eval_id(self) -> str:
        """Generate unique evaluation ID"""
        return f"eval_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def trigger_retry(self, result: EvaluationResult) -> Dict:
        """Trigger retry logic based on evaluation"""
        return {
            'action': 'RETRY',
            'reason': result.reasoning,
            'recommendations': result.recommendations,
            'retry_count': result.retry_count + 1
        }
    
    def reject_with_reason(self, result: EvaluationResult) -> Dict:
        """Reject content with detailed reason"""
        return {
            'action': 'REJECT',
            'reason': result.reasoning,
            'hallucinations': result.hallucinations_detected,
            'confidence': result.confidence
        }
    
    def request_validation(self, result: EvaluationResult) -> Dict:
        """Request human validation"""
        return {
            'action': 'VALIDATE',
            'reason': result.reasoning,
            'confidence': result.confidence,
            'flags': [
                f"Hallucination score: {result.hallucination_score:.2f}",
                f"Consistency score: {result.consistency_score:.2f}"
            ]
        }
    
    def to_structured_output(self, result: EvaluationResult) -> Dict:
        """
        Convert evaluation result to structured JSON output format
        
        Returns enterprise-grade structured response:
        {
          "answer": "...",
          "confidence": 0.82,
          "source_quality": 0.74,
          "validation_status": "PASS"
        }
        """
        return {
            "answer": result.answer,
            "confidence": round(result.confidence, 2),
            "source_quality": round(result.source_quality, 2),
            "validation_status": result.validation_status.value,
            "metadata": {
                "hallucination_score": round(result.hallucination_score, 2),
                "consistency_score": round(result.consistency_score, 2),
                "factual_accuracy": round(result.factual_accuracy, 2),
                "sources_verified": result.sources_verified,
                "contradictions_found": result.contradictions_found,
                "retry_count": result.retry_count
            },
            "quality_breakdown": {
                "content_quality": round(result.content_quality, 2),
                "summary_quality": round(result.summary_quality, 2),
                "information_density": round(result.information_density, 2),
                "coherence": round(result.coherence, 2)
            },
            "reasoning": result.reasoning,
            "recommendations": result.recommendations
        }
