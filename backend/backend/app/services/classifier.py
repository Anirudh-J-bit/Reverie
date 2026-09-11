import re
from typing import Dict, Any

class TaskClassifier:
    """
    Analyzes user prompts and classifies task complexity into: LOW, MEDIUM, or HIGH.
    """
    
    # Keyword patterns for complexity detection
    HIGH_COMPLEXITY_PATTERNS = [
        r"\banalyze\b", r"\bcompare\b", r"\bproof\b", r"\brefactor\b", 
        r"\barchitect\b", r"\bbenchmark\b", r"\bdataset\b", r"\bresearch paper\b",
        r"\boptimize\b", r"\bdesign pattern\b", r"\bsecurity audit\b"
    ]
    
    MEDIUM_COMPLEXITY_PATTERNS = [
        r"\bexplain\b", r"\bhow to\b", r"\bsummarize\b", r"\bwrite a function\b",
        r"\bdebug\b", r"\bdifference between\b", r"\bexample of\b"
    ]

    @classmethod
    def classify(cls, prompt: str) -> Dict[str, Any]:
        text_lower = prompt.lower()
        word_count = len(prompt.split())
        
        # Check for code blocks or high complexity indicators
        has_code = bool(re.search(r"```|def |class |function|import |SELECT ", prompt))
        high_matches = sum(1 for p in cls.HIGH_COMPLEXITY_PATTERNS if re.search(p, text_lower))
        med_matches = sum(1 for p in cls.MEDIUM_COMPLEXITY_PATTERNS if re.search(p, text_lower))

        # Decision Matrix
        if word_count > 300 or high_matches >= 2 or (has_code and word_count > 100):
            complexity = "HIGH"
            reason = "Long context, complex reasoning, or multi-step code analysis requested."
        elif word_count > 50 or med_matches >= 1 or high_matches == 1 or has_code:
            complexity = "MEDIUM"
            reason = "Moderate length or standard technical explanation/coding task."
        else:
            complexity = "LOW"
            reason = "Short factual or simple query."

        return {
            "complexity": complexity,
            "word_count": word_count,
            "has_code": has_code,
            "reason": reason
        }
        