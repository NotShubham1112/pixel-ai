"""
Offline inference engine for emotion-aware LLM on Raspberry Pi.
Integrates with llama.cpp for optimized performance.
"""

import subprocess
import json
from typing import Dict, Optional
from pathlib import Path
from emotion_prompt_template import EmotionPromptTemplate
from safety_filter import SafetyFilter
from memory_manager import MemoryManager


class InferenceEngine:
    """Offline inference engine for Raspberry Pi deployment."""
    
    def __init__(
        self,
        model_path: str,
        llama_cpp_path: str = "./llama.cpp/build/bin/main",
        n_ctx: int = 2048,
        n_threads: int = 4,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 300
    ):
        """Initialize inference engine with llama.cpp integration."""
        self.model_path = Path(model_path)
        self.llama_cpp_path = Path(llama_cpp_path)
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        
        self.safety_filter = SafetyFilter()
        self.memory_manager = MemoryManager()
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        print(f"✓ Inference engine initialized - Model: {self.model_path}")
    
    def generate_response(
        self, emotion: str, confidence: float, age_group: int, 
        question: str, use_memory: bool = True
    ) -> Dict:
        """Generate emotion-aware response with safety filtering."""
        # Safety check
        safety_result = self.safety_filter.filter_input(question, age_group)
        
        if not safety_result.is_safe:
            return {
                "response": self.safety_filter.get_refusal_response(safety_result.severity, age_group),
                "safety_filtered": True
            }
        
        # Get memory context
        memory_context = self.memory_manager.get_context() if use_memory else None
        
        # Create prompt
        prompt = EmotionPromptTemplate.create_prompt(
            emotion, confidence, age_group, question, memory_context
        )
        
        # Generate response
        response_text = self._call_llama_cpp(prompt)
        
        # Validate output
        validation = self.safety_filter.validate_output(response_text)
        if not validation.is_safe:
            response_text = "I'm having trouble answering that. Can you ask something else? 😊"
        
        # Store in memory
        if use_memory:
            self.memory_manager.add_interaction(emotion, question, response_text)
        
        return {
            "response": response_text,
            "emotion": emotion,
            "confidence": confidence,
            "age_group": age_group,
            "used_memory": use_memory
        }
    
    def _call_llama_cpp(self, prompt: str) -> str:
        """Call llama.cpp for inference."""
        cmd = [
            str(self.llama_cpp_path), "-m", str(self.model_path),
            "-p", prompt, "-n", str(self.max_tokens),
            "-t", str(self.n_threads), "-c", str(self.n_ctx),
            "--temp", str(self.temperature), "--top-p", str(self.top_p),
            "--no-display-prompt", "-ngl", "0"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout.strip() if result.returncode == 0 else "I'm having trouble right now."
        except Exception as e:
            print(f"⚠ Inference error: {e}")
            return "Sorry, I'm having trouble. Please try again!"


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Path to GGUF model")
    parser.add_argument("--emotion", default="happy", help="Emotion")
    parser.add_argument("--age", type=int, default=9, help="Age")
    parser.add_argument("--question", default="Why is the sky blue?", help="Question")
    args = parser.parse_args()
    
    engine = InferenceEngine(args.model)
    result = engine.generate_response(args.emotion, 0.85, args.age, args.question)
    
    print(f"\nQuestion: {args.question}")
    print(f"Response: {result['response']}")
