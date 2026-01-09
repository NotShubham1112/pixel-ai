"""
Emotion-aware prompt template for child-friendly LLM responses.
Structures input with emotion context and memory for consistent, safe outputs.
"""

from typing import Dict, Optional, List


class EmotionPromptTemplate:
    """Generates structured prompts for emotion-aware AI responses."""
    
    SYSTEM_PROMPT = """You are Pixel, a professional and friendly AI companion designed for children and students (ages 8-16). Your personality is helpful, calm, supportive, and clear, similar to an expert tutor or the Claude AI assistant.

Your role is to:
1. Use professional but accessible language.
2. Structure your knowledge using **Standard Markdown** (Headings, Bold text, Bullet points).
3. Provide detailed, passage-style explanations for educational topics (like Math, Science, or History).
4. Use # for main titles, ## for sections, and ### for sub-sections.
5. Encourage curiosity and critical thinking.

IMPORTANT SAFETY & STYLE RULES:
- Never give medical, legal, or therapeutic advice.
- Never discuss adult topics or harmful content.
- Keep responses engaging but structured. 
- Avoid excessive emoji spam; use them sparingly for warmth.
- If you don't know something, be honest: "I'm not exactly sure about that, but we could look it up together!"

Always respond in a clean, structured Markdown format."""

    EMOTION_CONTEXT = {
        "happy": "The child seems happy and cheerful. Match their positive energy!",
        "sad": "The child seems sad. Be gentle, supportive, and validating.",
        "angry": "The child seems upset or frustrated. Stay calm and help them feel heard.",
        "surprised": "The child seems surprised or amazed. Share their excitement!",
        "neutral": "The child seems calm and neutral. Respond naturally.",
        "confused": "The child seems confused. Be patient and explain clearly.",
        "excited": "The child seems very excited! Match their enthusiasm!",
        "worried": "The child seems worried or anxious. Be reassuring and calm."
    }
    
    AGE_GUIDELINES = {
        (5, 7): "Use very simple words. Short sentences. Concrete examples. Lots of encouragement.",
        (8, 10): "Use clear language. Explain new words. Use relatable examples from school and play.",
        (11, 13): "Use more complex vocabulary. Encourage critical thinking. Relate to their interests.",
        (14, 16): "Use mature but friendly language. Encourage deeper exploration. Respect their growing independence."
    }
    
    @classmethod
    def get_age_guideline(cls, age: int) -> str:
        """Get age-appropriate language guideline."""
        for (min_age, max_age), guideline in cls.AGE_GUIDELINES.items():
            if min_age <= age <= max_age:
                return guideline
        return cls.AGE_GUIDELINES[(8, 10)]  # Default to middle range
    
    @classmethod
    def format_memory_context(cls, memory: Optional[Dict] = None) -> str:
        """Format memory context for the prompt."""
        if not memory:
            return "This is a new conversation with no previous context."
        
        parts = []
        if memory.get("name"):
            parts.append(f"Child's name: {memory['name']}")
        if memory.get("favorite_color"):
            parts.append(f"Favorite color: {memory['favorite_color']}")
        if memory.get("favorite_subject"):
            parts.append(f"Favorite subject: {memory['favorite_subject']}")
        if memory.get("recent_topics"):
            topics = ", ".join(memory["recent_topics"][-3:])  # Last 3 topics
            parts.append(f"Recently discussed: {topics}")
        
        return "Previous context: " + "; ".join(parts) if parts else "This is a new conversation."
    
    @classmethod
    def create_prompt(
        cls,
        emotion: str,
        confidence: float,
        age_group: int,
        question: str,
        memory: Optional[Dict] = None
    ) -> str:
        """
        Create a complete prompt for the LLM.
        
        Args:
            emotion: Detected emotion (happy, sad, angry, etc.)
            confidence: Confidence score (0.0-1.0)
            age_group: Child's age (5-16)
            question: The child's question or statement
            memory: Optional memory context from previous interactions
            
        Returns:
            Formatted prompt string ready for LLM inference
        """
        emotion_context = cls.EMOTION_CONTEXT.get(emotion, cls.EMOTION_CONTEXT["neutral"])
        age_guideline = cls.get_age_guideline(age_group)
        memory_context = cls.format_memory_context(memory)
        
        # Confidence-based emotion reliability
        emotion_reliability = "high" if confidence >= 0.7 else "moderate" if confidence >= 0.5 else "low"
        
        prompt = f"""{cls.SYSTEM_PROMPT}

---
CURRENT CONTEXT:
- Detected emotion: {emotion} (confidence: {emotion_reliability})
- Emotion guidance: {emotion_context}
- Child's age: {age_group} years old
- Language guideline: {age_guideline}
- {memory_context}

---
CHILD'S MESSAGE:
{question}

---
YOUR RESPONSE (keep it under 300 characters, friendly and age-appropriate):"""

        return prompt
    
    @classmethod
    def create_chat_messages(
        cls,
        emotion: str,
        confidence: float,
        age_group: int,
        question: str,
        history: Optional[List[Dict]] = None,
        memory_stats: Optional[Dict] = None
    ) -> List[Dict[str, str]]:
        """
        Create a list of messages for Chat Completion API.
        """
        emotion_context = cls.EMOTION_CONTEXT.get(emotion, cls.EMOTION_CONTEXT["neutral"])
        age_guideline = cls.get_age_guideline(age_group)
        memory_context = cls.format_memory_context(memory_stats)
        emotion_reliability = "high" if confidence >= 0.7 else "moderate" if confidence >= 0.5 else "low"
        
        system_content = f"""{cls.SYSTEM_PROMPT}

CONTEXT:
- Emotion: {emotion} ({emotion_reliability})
- Guidance: {emotion_context}
- Age: {age_group}
- Language: {age_guideline}
- {memory_context}"""

        messages = [{"role": "system", "content": system_content}]
        
        # Add history (alternating user/assistant)
        if history:
            for item in history:
                messages.append({"role": "user", "content": item.get('question', '')})
                # Note: 'response' in MemoryManager, 'content' in Chat API. We map 'response' -> 'content'
                messages.append({"role": "assistant", "content": item.get('response', '')})
                
        # Add current question
        messages.append({"role": "user", "content": question})
        
        return messages
    
    @classmethod
    def create_training_example(
        cls,
        emotion: str,
        confidence: float,
        age_group: int,
        question: str,
        response: str,
        memory: Optional[Dict] = None
    ) -> Dict:
        """
        Create a training example in the required format.
        
        Returns:
            Dictionary with instruction, input, and output fields
        """
        return {
            "instruction": cls.SYSTEM_PROMPT,
            "input": {
                "emotion": emotion,
                "confidence": confidence,
                "age_group": age_group,
                "question": question,
                "memory": memory or {}
            },
            "output": response
        }


# Example usage
if __name__ == "__main__":
    # Example 1: Happy child asking about space
    prompt1 = EmotionPromptTemplate.create_prompt(
        emotion="excited",
        confidence=0.85,
        age_group=9,
        question="Why is the sky blue?",
        memory={"name": "Alex", "favorite_subject": "Science"}
    )
    print("=== Example 1: Excited child ===")
    print(prompt1)
    print("\n" + "="*50 + "\n")
    
    # Example 2: Sad child needing support
    prompt2 = EmotionPromptTemplate.create_prompt(
        emotion="sad",
        confidence=0.92,
        age_group=7,
        question="I don't have any friends at school",
        memory={"name": "Sam"}
    )
    print("=== Example 2: Sad child ===")
    print(prompt2)
    print("\n" + "="*50 + "\n")
    
    # Example 3: Training example format
    training_ex = EmotionPromptTemplate.create_training_example(
        emotion="confused",
        confidence=0.78,
        age_group=11,
        question="What is gravity?",
        response="Great question! Gravity is like an invisible force that pulls things together. It's why when you drop a ball, it falls down instead of floating away. Earth's gravity keeps us on the ground and the Moon orbiting around us. Want to know more about how it works?"
    )
    print("=== Training Example Format ===")
    import json
    print(json.dumps(training_ex, indent=2))
