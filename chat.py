"""
Interactive Terminal Chat Interface for Emotion LLM
Features:
- Real-time chat with emotion detection
- Automatic conversation saving to dataset
- Incremental training with new conversations
- Raspberry Pi compatible
- Safety filtering
- Memory management
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from inference_engine import InferenceEngine
except ImportError:
    InferenceEngine = None

from safety_filter import SafetyFilter
from memory_manager import MemoryManager
from emotion_prompt_template import EmotionPromptTemplate


class ChatInterface:
    """Interactive chat interface with training integration."""
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        dataset_path: str = "chat_training_data.json",
        auto_save: bool = True
    ):
        """
        Initialize chat interface.
        
        Args:
            model_path: Path to GGUF model (optional for dataset-only mode)
            dataset_path: Path to save training conversations
            auto_save: Automatically save conversations to dataset
        """
        self.model_path = model_path
        self.dataset_path = dataset_path
        self.auto_save = auto_save
        
        # Initialize components
        self.safety_filter = SafetyFilter()
        self.memory_manager = MemoryManager(storage_path="chat_memory.json")
        
        # Initialize inference engine if model provided
        self.engine = None
        if model_path and Path(model_path).exists() and InferenceEngine:
            try:
                self.engine = InferenceEngine(model_path)
                print(f"✓ Model loaded: {model_path}")
            except Exception as e:
                print(f"⚠ Could not load model: {e}")
                print("  Running in dataset-only mode")
        
        # Load or create dataset
        self.dataset = self._load_dataset()
        
        # Chat state
        self.current_emotion = "neutral"
        self.current_age = 9
        self.conversation_history = []
        
    def _load_dataset(self) -> dict:
        """Load existing dataset or create new one."""
        if Path(self.dataset_path).exists():
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "dataset_info": {
                "version": "1.0.0",
                "total_examples": 0,
                "created_at": datetime.now().isoformat(),
                "source": "interactive_chat"
            },
            "examples": []
        }
    
    def _save_dataset(self):
        """Save dataset to file."""
        self.dataset["dataset_info"]["total_examples"] = len(self.dataset["examples"])
        self.dataset["dataset_info"]["last_updated"] = datetime.now().isoformat()
        
        with open(self.dataset_path, 'w', encoding='utf-8') as f:
            json.dump(self.dataset, f, indent=2, ensure_ascii=False)
    
    def add_to_dataset(self, emotion: str, question: str, response: str, age: int):
        """Add conversation to training dataset."""
        example = {
            "instruction": EmotionPromptTemplate.SYSTEM_PROMPT,
            "input": {
                "emotion": emotion,
                "confidence": 0.85,  # Default confidence
                "age_group": age,
                "question": question,
                "memory": self.memory_manager.get_context()
            },
            "output": response,
            "metadata": {
                "emotion_category": emotion,
                "age_group": self._get_age_group(age),
                "safety_level": "safe",
                "response_type": "chat",
                "includes_memory": bool(self.memory_manager.get_context()),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        self.dataset["examples"].append(example)
        
        if self.auto_save:
            self._save_dataset()
    
    def _get_age_group(self, age: int) -> str:
        """Convert age to age group."""
        if age <= 7:
            return "5-7"
        elif age <= 10:
            return "8-10"
        elif age <= 13:
            return "11-13"
        else:
            return "14-16"
    
    def generate_response(self, question: str) -> str:
        """Generate response using model or fallback."""
        # Safety check
        safety_result = self.safety_filter.filter_input(question, self.current_age)
        
        if not safety_result.is_safe:
            return self.safety_filter.get_refusal_response(safety_result.severity, self.current_age)
        
        if safety_result.reason and "redirect" in safety_result.reason.lower():
            topic = safety_result.reason.split(":")[-1].strip()
            return self.safety_filter.get_redirect_response(topic, self.current_age)
        
        # Generate with model if available
        if self.engine:
            try:
                result = self.engine.generate_response(
                    emotion=self.current_emotion,
                    confidence=0.85,
                    age_group=self.current_age,
                    question=question,
                    use_memory=True
                )
                return result["response"]
            except Exception as e:
                print(f"⚠ Model error: {e}")
                return self._fallback_response(question)
        else:
            return self._fallback_response(question)
    
    def _fallback_response(self, question: str) -> str:
        """Simple fallback response when no model available."""
        responses = [
            "That's an interesting question! I'm still learning, so I might not have the best answer yet.",
            "Great question! Let me think about that...",
            "I'm not sure about that, but it's a good thing to be curious about!",
            "That's something I'd like to learn more about too!",
        ]
        import random
        return random.choice(responses)
    
    def setup_profile(self):
        """Set up user profile."""
        print("\n" + "="*60)
        print("PROFILE SETUP")
        print("="*60)
        
        name = input("What's your name? (or press Enter to skip): ").strip()
        if name:
            age_input = input("How old are you? (5-16): ").strip()
            try:
                age = int(age_input)
                if 5 <= age <= 16:
                    self.current_age = age
                else:
                    print("Using default age: 9")
            except:
                print("Using default age: 9")
            
            # Ask for consent
            consent = input("\nCan I remember your name and preferences? (yes/no): ").strip().lower()
            if consent == "yes":
                self.memory_manager.give_consent(True)
                self.memory_manager.set_user_profile(name=name, age=self.current_age)
                
                color = input("What's your favorite color? (optional): ").strip()
                if color:
                    self.memory_manager.set_user_profile(favorite_color=color)
                
                subject = input("What's your favorite subject? (optional): ").strip()
                if subject:
                    self.memory_manager.set_user_profile(favorite_subject=subject)
                
                print(f"\n✓ Profile saved! Hi {name}!")
            else:
                print("\n✓ No problem! We can chat without saving your info.")
        
        print("="*60)
    
    def set_emotion(self):
        """Manually set emotion (for testing)."""
        emotions = ["happy", "sad", "angry", "surprised", "neutral", "confused", "excited", "worried"]
        print("\nAvailable emotions:", ", ".join(emotions))
        emotion = input("Set emotion (or press Enter for neutral): ").strip().lower()
        
        if emotion in emotions:
            self.current_emotion = emotion
            print(f"✓ Emotion set to: {emotion}")
        else:
            self.current_emotion = "neutral"
            print("✓ Emotion set to: neutral")
    
    def chat_loop(self):
        """Main chat loop."""
        print("\n" + "="*60)
        print("CHAT MODE")
        print("="*60)
        print("Commands:")
        print("  /emotion - Change emotion")
        print("  /stats   - View statistics")
        print("  /save    - Save dataset")
        print("  /train   - Start training (if configured)")
        print("  /quit    - Exit chat")
        print("="*60)
        
        while True:
            try:
                # Get user input
                user_input = input(f"\n[{self.current_emotion}] You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    if user_input == "/quit":
                        print("\nGoodbye! 👋")
                        break
                    elif user_input == "/emotion":
                        self.set_emotion()
                        continue
                    elif user_input == "/stats":
                        self.show_stats()
                        continue
                    elif user_input == "/save":
                        self._save_dataset()
                        print(f"✓ Dataset saved: {len(self.dataset['examples'])} examples")
                        continue
                    elif user_input == "/train":
                        self.start_training()
                        continue
                    else:
                        print("Unknown command. Type /quit to exit.")
                        continue
                
                # Generate response
                response = self.generate_response(user_input)
                print(f"AI: {response}")
                
                # Add to memory
                self.memory_manager.add_interaction(
                    self.current_emotion,
                    user_input,
                    response
                )
                
                # Add to dataset
                self.add_to_dataset(
                    self.current_emotion,
                    user_input,
                    response,
                    self.current_age
                )
                
                # Store in conversation history
                self.conversation_history.append({
                    "emotion": self.current_emotion,
                    "question": user_input,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n⚠ Error: {e}")
                continue
    
    def show_stats(self):
        """Show chat statistics."""
        print("\n" + "="*60)
        print("STATISTICS")
        print("="*60)
        print(f"Dataset examples: {len(self.dataset['examples'])}")
        print(f"Current session: {len(self.conversation_history)} messages")
        print(f"Memory stats: {self.memory_manager.get_stats()}")
        print(f"Safety blocks: {self.safety_filter.get_stats()}")
        print("="*60)
    
    def start_training(self):
        """Start incremental training with new data."""
        print("\n" + "="*60)
        print("TRAINING")
        print("="*60)
        
        if len(self.dataset['examples']) < 10:
            print("⚠ Need at least 10 examples to train. Keep chatting!")
            return
        
        print(f"Ready to train with {len(self.dataset['examples'])} examples")
        print("\nTo train the model, run:")
        print(f"  python train_lora.py --dataset {self.dataset_path} --epochs 1")
        print("\nNote: Training requires GPU and takes 1-2 hours")
        print("="*60)
    
    def run(self):
        """Run the chat interface."""
        print("="*60)
        print("EMOTION LLM - INTERACTIVE CHAT")
        print("="*60)
        print(f"Model: {'Loaded' if self.engine else 'Dataset-only mode'}")
        print(f"Dataset: {self.dataset_path}")
        print(f"Auto-save: {'Enabled' if self.auto_save else 'Disabled'}")
        print("="*60)
        
        # Setup profile
        self.setup_profile()
        
        # Start chat
        self.chat_loop()
        
        # Save on exit
        if self.auto_save:
            self._save_dataset()
            print(f"\n✓ Saved {len(self.dataset['examples'])} examples to {self.dataset_path}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Interactive chat with Emotion LLM")
    parser.add_argument("--model", type=str, help="Path to GGUF model (optional)")
    parser.add_argument("--dataset", type=str, default="chat_training_data.json", 
                       help="Path to save training data")
    parser.add_argument("--no-auto-save", action="store_true", 
                       help="Disable automatic dataset saving")
    
    args = parser.parse_args()
    
    # Create chat interface
    chat = ChatInterface(
        model_path=args.model,
        dataset_path=args.dataset,
        auto_save=not args.no_auto_save
    )
    
    # Run
    chat.run()


if __name__ == "__main__":
    main()
