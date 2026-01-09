"""
Safety filter for child-friendly content moderation.
Filters inappropriate inputs and validates outputs.
"""

import re
from typing import Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class SafetyResult:
    """Result of safety check."""
    is_safe: bool
    reason: Optional[str] = None
    filtered_text: Optional[str] = None
    severity: str = "none"  # none, low, medium, high


class SafetyFilter:
    """Content moderation for child-safe interactions."""
    
    # Forbidden topics and keywords
    FORBIDDEN_KEYWORDS = {
        "high": [
            # Violence and harm
            "kill", "murder", "suicide", "hurt yourself", "self-harm",
            # Adult content
            "sex", "porn", "nude", "naked",
            # Substances
            "drug", "cocaine", "heroin", "meth",
            # Weapons
            "gun", "weapon", "bomb", "explosive"
        ],
        "medium": [
            # Potentially concerning
            "hate", "stupid", "idiot", "dumb",
            "alcohol", "beer", "wine", "drunk",
            "cigarette", "smoking", "vape",
            # Personal info requests
            "address", "phone number", "credit card", "password"
        ],
        "low": [
            # Mild concerns
            "scared", "afraid", "worried", "anxious",
            "sad", "depressed", "lonely"
        ]
    }
    
    # Topics requiring redirection to adults
    REDIRECT_TOPICS = [
        "medical", "doctor", "medicine", "sick", "disease",
        "therapy", "counselor", "mental health",
        "legal", "lawyer", "police",
        "money", "buy", "purchase", "credit"
    ]
    
    # Age-inappropriate complexity
    COMPLEX_TOPICS = {
        (5, 7): ["quantum", "calculus", "philosophy", "politics", "economics"],
        (8, 10): ["quantum physics", "advanced calculus", "existentialism"],
        (11, 13): ["quantum mechanics", "differential equations"]
    }
    
    def __init__(self):
        self.blocked_count = 0
        self.redirected_count = 0
        
    def check_forbidden_content(self, text: str) -> SafetyResult:
        """Check for forbidden keywords."""
        text_lower = text.lower()
        
        # Check high severity
        for keyword in self.FORBIDDEN_KEYWORDS["high"]:
            if keyword in text_lower:
                self.blocked_count += 1
                return SafetyResult(
                    is_safe=False,
                    reason=f"Contains forbidden content: {keyword}",
                    severity="high"
                )
        
        # Check medium severity
        for keyword in self.FORBIDDEN_KEYWORDS["medium"]:
            if keyword in text_lower:
                return SafetyResult(
                    is_safe=True,  # Allow but flag
                    reason=f"Contains sensitive content: {keyword}",
                    severity="medium"
                )
        
        # Check low severity (emotional distress)
        for keyword in self.FORBIDDEN_KEYWORDS["low"]:
            if keyword in text_lower:
                return SafetyResult(
                    is_safe=True,
                    reason=f"Emotional content detected: {keyword}",
                    severity="low"
                )
        
        return SafetyResult(is_safe=True)
    
    def check_redirect_needed(self, text: str) -> Tuple[bool, Optional[str]]:
        """Check if question should be redirected to adults."""
        text_lower = text.lower()
        
        for topic in self.REDIRECT_TOPICS:
            if topic in text_lower:
                self.redirected_count += 1
                return True, topic
        
        return False, None
    
    def check_age_appropriate(self, text: str, age: int) -> SafetyResult:
        """Check if content complexity is age-appropriate."""
        text_lower = text.lower()
        
        for (min_age, max_age), topics in self.COMPLEX_TOPICS.items():
            if age >= min_age and age <= max_age:
                for topic in topics:
                    if topic in text_lower:
                        return SafetyResult(
                            is_safe=True,
                            reason=f"Topic '{topic}' may be too complex for age {age}",
                            severity="low"
                        )
        
        return SafetyResult(is_safe=True)
    
    def filter_input(self, text: str, age: int) -> SafetyResult:
        """
        Filter user input for safety.
        
        Args:
            text: User's question or statement
            age: User's age
            
        Returns:
            SafetyResult with safety status and recommendations
        """
        # Check forbidden content
        forbidden_check = self.check_forbidden_content(text)
        if not forbidden_check.is_safe:
            return forbidden_check
        
        # Check if redirect needed
        needs_redirect, topic = self.check_redirect_needed(text)
        if needs_redirect:
            return SafetyResult(
                is_safe=True,
                reason=f"Should redirect to adult for topic: {topic}",
                severity="medium"
            )
        
        # Check age appropriateness
        age_check = self.check_age_appropriate(text, age)
        
        # Return most severe result
        if forbidden_check.severity != "none":
            return forbidden_check
        elif age_check.severity != "none":
            return age_check
        
        return SafetyResult(is_safe=True)
    
    def validate_output(self, response: str, max_length: int = 300) -> SafetyResult:
        """
        Validate AI response for safety and quality.
        
        Args:
            response: AI's generated response
            max_length: Maximum allowed response length
            
        Returns:
            SafetyResult with validation status
        """
        # Check length
        if len(response) > max_length:
            return SafetyResult(
                is_safe=False,
                reason=f"Response too long: {len(response)} > {max_length}",
                filtered_text=response[:max_length] + "...",
                severity="low"
            )
        
        # Check for forbidden content in response
        forbidden_check = self.check_forbidden_content(response)
        if not forbidden_check.is_safe:
            return SafetyResult(
                is_safe=False,
                reason="Response contains inappropriate content",
                severity="high"
            )
        
        # Check for uncertainty statements (good practice)
        uncertainty_phrases = [
            "i'm not sure", "i don't know", "i might be wrong",
            "ask a parent", "ask a teacher", "ask an adult"
        ]
        has_uncertainty = any(phrase in response.lower() for phrase in uncertainty_phrases)
        
        return SafetyResult(
            is_safe=True,
            reason="Includes uncertainty statement" if has_uncertainty else None
        )
    
    def get_refusal_response(self, severity: str, age: int) -> str:
        """Generate age-appropriate refusal response."""
        if age <= 10:
            return "I can't help with that question. Please ask a parent or teacher instead! 😊"
        else:
            return "I'm not able to answer that question. For important topics like this, it's best to talk to a trusted adult, parent, or teacher."
    
    def get_redirect_response(self, topic: str, age: int) -> str:
        """Generate age-appropriate redirect response."""
        if age <= 10:
            return f"That's an important question about {topic}! I think a parent, teacher, or doctor would be the best person to ask about this."
        else:
            return f"For questions about {topic}, I'd recommend talking to a qualified professional like a parent, teacher, or doctor. They can give you better guidance than I can!"
    
    def get_stats(self) -> dict:
        """Get safety filter statistics."""
        return {
            "blocked_count": self.blocked_count,
            "redirected_count": self.redirected_count
        }


# Example usage
if __name__ == "__main__":
    filter = SafetyFilter()
    
    # Test cases
    test_cases = [
        ("Why is the sky blue?", 8, "safe"),
        ("I want to hurt myself", 12, "block"),
        ("My stomach hurts", 7, "redirect"),
        ("How do I make a bomb?", 14, "block"),
        ("I'm feeling sad today", 9, "allow_with_care"),
        ("What's quantum physics?", 6, "age_check"),
    ]
    
    print("="*60)
    print("SAFETY FILTER TEST CASES")
    print("="*60)
    
    for question, age, expected in test_cases:
        result = filter.filter_input(question, age)
        print(f"\nQuestion: '{question}' (Age: {age})")
        print(f"Expected: {expected}")
        print(f"Safe: {result.is_safe}")
        print(f"Severity: {result.severity}")
        print(f"Reason: {result.reason}")
        
        if not result.is_safe:
            print(f"Refusal: {filter.get_refusal_response(result.severity, age)}")
        elif result.reason and "redirect" in result.reason.lower():
            topic = result.reason.split(":")[-1].strip()
            print(f"Redirect: {filter.get_redirect_response(topic, age)}")
    
    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    print(filter.get_stats())
