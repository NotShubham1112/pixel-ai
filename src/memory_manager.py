"""
Memory manager for ethical, privacy-preserving conversation context.
Stores short-term and consented long-term user information.
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class MemoryManager:
    """Manages conversation memory with privacy controls."""
    
    def __init__(self, storage_path: str = "data/user_memory.json", max_short_term: int = 10):
        """
        Initialize memory manager.
        
        Args:
            storage_path: Path to store memory data
            max_short_term: Maximum number of recent interactions to keep
        """
        self.storage_path = Path(storage_path)
        self.max_short_term = max_short_term
        self.memory = self._load_memory()
        
    def _load_memory(self) -> Dict:
        """Load memory from storage."""
        if self.storage_path.exists():
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "user_profile": {
                "name": None,
                "age": None,
                "favorite_color": None,
                "favorite_subject": None,
                "consent_given": False,
                "created_at": datetime.now().isoformat()
            },
            "short_term": [],  # Last N interactions
            "long_term": {
                "topics_discussed": [],
                "interests": [],
                "learning_goals": []
            },
            "metadata": {
                "total_interactions": 0,
                "last_interaction": None
            }
        }
    
    def _save_memory(self):
        """Save memory to storage."""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def set_user_profile(self, name: Optional[str] = None, age: Optional[int] = None,
                        favorite_color: Optional[str] = None, favorite_subject: Optional[str] = None):
        """
        Set user profile information (requires consent).
        
        Args:
            name: User's name
            age: User's age
            favorite_color: User's favorite color
            favorite_subject: User's favorite subject
        """
        if not self.memory["user_profile"]["consent_given"]:
            print("⚠ Warning: User consent not given for storing personal information")
            return False
        
        if name:
            self.memory["user_profile"]["name"] = name
        if age:
            self.memory["user_profile"]["age"] = age
        if favorite_color:
            self.memory["user_profile"]["favorite_color"] = favorite_color
        if favorite_subject:
            self.memory["user_profile"]["favorite_subject"] = favorite_subject
        
        self._save_memory()
        return True
    
    def give_consent(self, consent: bool = True):
        """
        Set user consent for storing personal information.
        
        Args:
            consent: Whether user gives consent
        """
        self.memory["user_profile"]["consent_given"] = consent
        self._save_memory()
        print(f"✓ Consent {'given' if consent else 'revoked'}")
    
    def add_interaction(self, emotion: str, question: str, response: str):
        """
        Add a new interaction to short-term memory.
        
        Args:
            emotion: Detected emotion
            question: User's question
            response: AI's response
        """
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion,
            "question": question,
            "response": response
        }
        
        # Add to short-term memory
        self.memory["short_term"].append(interaction)
        
        # Keep only last N interactions
        if len(self.memory["short_term"]) > self.max_short_term:
            self.memory["short_term"] = self.memory["short_term"][-self.max_short_term:]
        
        # Update metadata
        self.memory["metadata"]["total_interactions"] += 1
        self.memory["metadata"]["last_interaction"] = datetime.now().isoformat()
        
        # Extract topics for long-term memory
        self._extract_topics(question)
        
        self._save_memory()
    
    def _extract_topics(self, question: str):
        """Extract and store topics from questions."""
        # Simple keyword extraction (in production, use NLP)
        topic_keywords = ["space", "math", "science", "art", "music", "animals", "sports", 
                         "reading", "coding", "history", "geography"]
        
        question_lower = question.lower()
        for keyword in topic_keywords:
            if keyword in question_lower:
                if keyword not in self.memory["long_term"]["topics_discussed"]:
                    self.memory["long_term"]["topics_discussed"].append(keyword)
    
    def get_context(self) -> Dict:
        """
        Get memory context for prompt generation.
        
        Returns:
            Dictionary with relevant memory context
        """
        context = {}
        
        # User profile (only if consent given)
        if self.memory["user_profile"]["consent_given"]:
            profile = self.memory["user_profile"]
            if profile["name"]:
                context["name"] = profile["name"]
            if profile["favorite_color"]:
                context["favorite_color"] = profile["favorite_color"]
            if profile["favorite_subject"]:
                context["favorite_subject"] = profile["favorite_subject"]
        
        # Recent topics (last 3)
        recent_topics = self.memory["long_term"]["topics_discussed"][-3:]
        if recent_topics:
            context["recent_topics"] = recent_topics
        
        return context
    
    def get_recent_interactions(self, n: int = 5) -> List[Dict]:
        """
        Get N most recent interactions.
        
        Args:
            n: Number of interactions to retrieve
            
        Returns:
            List of recent interactions
        """
        return self.memory["short_term"][-n:]
    
    def clear_history(self):
        """Clear short-term memory (conversation history)."""
        self.memory["short_term"] = []
        self._save_memory()
        return True
    
    def clear_short_term(self):
        """Alias for clear_history."""
        return self.clear_history()
    
    def clear_all(self):
        """Clear all memory (requires confirmation in production)."""
        self.memory = {
            "user_profile": {
                "name": None,
                "age": None,
                "favorite_color": None,
                "favorite_subject": None,
                "consent_given": False,
                "created_at": datetime.now().isoformat()
            },
            "short_term": [],
            "long_term": {
                "topics_discussed": [],
                "interests": [],
                "learning_goals": []
            },
            "metadata": {
                "total_interactions": 0,
                "last_interaction": None
            }
        }
        self._save_memory()
        print("✓ All memory cleared")
    
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        return {
            "total_interactions": self.memory["metadata"]["total_interactions"],
            "short_term_count": len(self.memory["short_term"]),
            "topics_count": len(self.memory["long_term"]["topics_discussed"]),
            "has_profile": self.memory["user_profile"]["consent_given"],
            "last_interaction": self.memory["metadata"]["last_interaction"]
        }


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("MEMORY MANAGER DEMO")
    print("="*60)
    
    # Initialize memory manager
    memory = MemoryManager(storage_path="./demo_memory.json")
    
    # Give consent
    print("\n1. Giving consent for memory storage...")
    memory.give_consent(True)
    
    # Set user profile
    print("\n2. Setting user profile...")
    memory.set_user_profile(name="Alex", age=9, favorite_color="blue", favorite_subject="Science")
    
    # Add some interactions
    print("\n3. Adding interactions...")
    interactions = [
        ("happy", "Why is the sky blue?", "Great question! The sky looks blue because..."),
        ("curious", "Tell me about space!", "Space is amazing! It's the vast area beyond Earth..."),
        ("excited", "I love science!", "That's wonderful! Science helps us understand the world..."),
    ]
    
    for emotion, question, response in interactions:
        memory.add_interaction(emotion, question, response)
        print(f"  Added: {question[:30]}...")
    
    # Get context
    print("\n4. Getting memory context for next prompt...")
    context = memory.get_context()
    print(f"  Context: {json.dumps(context, indent=2)}")
    
    # Get stats
    print("\n5. Memory statistics...")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Get recent interactions
    print("\n6. Recent interactions...")
    recent = memory.get_recent_interactions(3)
    for i, interaction in enumerate(recent, 1):
        print(f"  {i}. [{interaction['emotion']}] {interaction['question'][:40]}...")
    
    print("\n" + "="*60)
    print("✓ Demo complete! Check demo_memory.json for stored data")
    print("="*60)
