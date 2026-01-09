"""
MAIN AI MIRROR SYSTEM
---------------------
This is the master script that runs the entire system on Raspberry Pi.
Integrates:
1. 2-bit LLM (Fast inference)
2. RAG System (Knowledge retrieval)
3. Emotion Engine (Prompt adaptation)
4. Safety Layer (Content filtering)
5. Memory System (User context)
"""

import sys
import time
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

# Initialize Rich Console
console = Console()

# Configuration
CONFIG = {
    "min_confidence": 0.5,
    "default_age": 9,
    "max_history": 10,
    "rag_enabled": False,
    "mock_llm_enabled": False
}

def print_system_status():
    console.print("\n" + "="*60, style="blue")
    console.print("🚀 STARTING AI MIRROR SYSTEM", style="bold cyan")
    console.print("="*60, style="blue")
    console.print(f"• Platform: {sys.platform}")
    console.print(f"• Python: {sys.version.split()[0]}")
    console.print(f"• RAG: {'Enabled' if CONFIG['rag_enabled'] else 'Disabled'}")

def main():
    print_system_status()
    
    # 1. LOAD COMPONENTS
    console.print("\n[1/5] Loading Safety & Memory Components...", style="bold yellow")
    try:
        from safety_filter import SafetyFilter
        from memory_manager import MemoryManager
        
        safety = SafetyFilter()
        memory = MemoryManager(storage_path="data/ai_mirror_memory.json")
        console.print("   ✓ Safety Filter active", style="green")
        console.print(f"   ✓ Memory active ({memory.get_stats()['total_interactions']} interactions)", style="green")
    except ImportError as e:
        console.print(f"   ❌ Failed to load components: {e}", style="bold red")
        sys.exit(1)

    # 2. INITIALIZE RAG
    console.print("\n[2/5] Initializing RAG Knowledge Base...", style="bold yellow")
    rag = None
    if CONFIG['rag_enabled']:
        try:
            from rag_system import RAGSystem
            rag = RAGSystem()
            doc_count = rag.collection.count()
            console.print(f"   ✓ RAG System ready ({doc_count} documents)", style="green")
            if doc_count == 0:
                console.print("   ⚠ Knowledge base empty! Run 'python build_knowledge_base.py'", style="yellow")
        except Exception as e:
            console.print(f"   ⚠ RAG failed (running without knowledge): {e}", style="yellow")

    # 3. LOAD LLM (Auto-select 2-bit)
    console.print("\n[3/5] Loading LLM...", style="bold yellow")
    llm = None
    try:
        if CONFIG.get('mock_llm_enabled'):
            raise ImportError("Mock mode enabled")
            
        try:
            from llama_cpp import Llama
        except ImportError:
            console.print("   Installing llama-cpp-python...", style="yellow")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "llama-cpp-python"])
            from llama_cpp import Llama
            
        # Find best model (Priority: Q2 > Q4 > Q5)
        model_path = None
        models_dir = Path("models")
        if models_dir.exists():
            for q in ["Q2", "Q4", "Q5"]:
                found = list(models_dir.glob(f"*{q}*.gguf"))
                if found:
                    model_path = found[0]
                    break
        
        if not model_path:
            raise FileNotFoundError("No model found in models/ directory!")
            
        console.print(f"   ✓ Loading {model_path.name}...", style="green")
        llm = Llama(
            model_path=str(model_path),
            n_ctx=2048,
            n_threads=4,  # Optimized for Pi 4/5
            verbose=False
        )
        console.print("   ✓ LLM Ready", style="green")
        
    except Exception as e:
        console.print(f"   ⚠ LLM load failed ({e}). using MOCK LLM for testing.", style="yellow")
        
        class MockLlama:
            def __call__(self, prompt, **kwargs):
                return {
                    'choices': [{
                        'text': " [MOCK] I heard you! I'm running in mock mode because the real brain couldn't load. How are you?"
                    }]
                }
            
            def create_chat_completion(self, messages, **kwargs):
                return {
                    'choices': [{
                        'message': {
                            'content': " [MOCK CHAT] I heard you! I'm running in mock mode because the real brain couldn't load. How are you?"
                        }
                    }]
                }
        llm = MockLlama()

    # 4. START LOOP
    console.print("\n[4/5] Starting Emotion Engine...", style="bold yellow")
    console.print("   ✓ Emotion Context: Ready", style="green")
    console.print("\n[5/5] System Ready! Waiting for input...", style="bold green")
    console.print("="*60 + "\n", style="blue")

    # Main Interaction Loop
    while True:
        try:
            # A. GET INPUT
            user_input = console.input("\n[bold green]You:[/bold green] ").strip()
            if not user_input: continue
            
            # COMMANDS
            if user_input.lower() in ['quit', 'exit']: break
            if user_input.lower() == '/reset':
                memory.clear_history()
                console.print("\n[bold yellow]✨ Conversation and memory context reset![/bold yellow]\n")
                continue

            start_time = time.time()

            # B. SAFETY CHECK (Input)
            safety_result = safety.filter_input(user_input, age=CONFIG['default_age'])
            if not safety_result.is_safe:
                print(f"DEBUG: Input Blocked. Reason: {safety_result.reason} | Severity: {safety_result.severity}")
                print("AI: I can't talk about that. Let's talk about something else! 😊")
                continue

            # C. RAG RETRIEVAL
            context = ""
            if rag:
                context = rag.augment_prompt(user_input, emotion="neutral", age=CONFIG['default_age'])
                # Extract just the context part if needed, or use the full augmented prompt

            # D. GENERATE RESPONSE
            # Use Chat Completion API for better instruction following with Qwen
            messages = []
            
            if rag and context:
                # If RAG is active, treating context as system info
                messages = [
                    {"role": "system", "content": "You are Pixel, a friendly AI companion. Use the provided context to answer."},
                    {"role": "user", "content": f"Context: {context}\n\nQuestion: {user_input}"}
                ]
            else:
                from emotion_prompt_template import EmotionPromptTemplate
                # Mock emotion
                current_emotion = "neutral" 
                emotion_confidence = 0.9
                
                # Fetch conversation history from memory
                history = memory.get_recent_interactions(n=CONFIG['max_history'])
                memory_stats = memory.get_context()
                
                messages = EmotionPromptTemplate.create_chat_messages(
                    emotion=current_emotion,
                    confidence=emotion_confidence,
                    age_group=CONFIG['default_age'],
                    question=user_input,
                    history=history,
                    memory_stats=memory_stats
                )

            # Check if using MockLLM or Real LLM
            if hasattr(llm, 'create_chat_completion'):
                response = llm.create_chat_completion(
                    messages=messages,
                    max_tokens=800,  # Allow for full explanations
                    temperature=0.7,
                    top_p=0.9,
                    top_k=40,
                    repeat_penalty=1.1,
                    stop=["User:", "Pixel:", "System:"],
                )
                answer = response['choices'][0]['message']['content'].strip()
            else:
                # Fallback for MockLLM
                print("DEBUG: Using Mock LLM fallback")
                answer = llm(str(messages))['choices'][0]['text']

            # E. SAFETY CHECK (Output)
            # Increase max length to 5000 to allow detailed educational answers
            out_safety = safety.validate_output(answer, max_length=5000)
            if not out_safety.is_safe:
                print(f"DEBUG: Output Blocked. Reason: {out_safety.reason} | Severity: {out_safety.severity}")
                print(f"DEBUG: BLOCKED TEXT: {answer}")
                answer = "I'm having a bit of trouble thinking right now. Ask me again?"

            # F. SAVE MEMORY
            memory.add_interaction("neutral", user_input, answer)

            # G. OUTPUT
            latency = time.time() - start_time
            console.print("\n" + "-"*40, style="blue")
            console.print("🤖 [bold cyan]Pixel:[/bold cyan]")
            
            # Render the response as Markdown
            md = Markdown(answer)
            console.print(md)
            
            console.print("-"*40, style="blue")
            console.print(f"    (⏱️ {latency:.2f}s)\n")

        except KeyboardInterrupt:
            console.print("\n[bold red]Shutting down...[/bold red]")
            break
        except Exception as e:
            console.print(f"\n❌ Error: {e}", style="bold red")

if __name__ == "__main__":
    main()
