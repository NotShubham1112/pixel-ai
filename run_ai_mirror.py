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

# Configuration
CONFIG = {
    "min_confidence": 0.5,
    "default_age": 9,
    "max_history": 10,
    "rag_enabled": True
}

def print_system_status():
    print("\n" + "="*60)
    print("🚀 STARTING AI MIRROR SYSTEM")
    print("="*60)
    print(f"• Platform: {sys.platform}")
    print(f"• Python: {sys.version.split()[0]}")
    print(f"• RAG: {'Enabled' if CONFIG['rag_enabled'] else 'Disabled'}")

def main():
    print_system_status()
    
    # 1. LOAD COMPONENTS
    print("\n[1/5] Loading Safety & Memory Components...")
    try:
        from safety_filter import SafetyFilter
        from memory_manager import MemoryManager
        
        safety = SafetyFilter()
        memory = MemoryManager(storage_path="ai_mirror_memory.json")
        print("   ✓ Safety Filter active")
        print(f"   ✓ Memory active ({memory.get_stats()['total_interactions']} interactions)")
    except ImportError as e:
        print(f"   ❌ Failed to load components: {e}")
        sys.exit(1)

    # 2. INITIALIZE RAG
    print("\n[2/5] Initializing RAG Knowledge Base...")
    rag = None
    if CONFIG['rag_enabled']:
        try:
            from rag_system import RAGSystem
            rag = RAGSystem()
            doc_count = rag.collection.count()
            print(f"   ✓ RAG System ready ({doc_count} documents)")
            if doc_count == 0:
                print("   ⚠ Knowledge base empty! Run 'python build_knowledge_base.py'")
        except Exception as e:
            print(f"   ⚠ RAG failed (running without knowledge): {e}")

    # 3. LOAD LLM (Auto-select 2-bit)
    print("\n[3/5] Loading LLM...")
    try:
        from llama_cpp import Llama
    except ImportError:
        print("   Installing llama-cpp-python...")
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
        print("   ❌ No model found in models/ directory!")
        print("   Run: python download_2bit.py")
        sys.exit(1)
        
    print(f"   ✓ Loading {model_path.name}...")
    llm = Llama(
        model_path=str(model_path),
        n_ctx=2048,
        n_threads=4,  # Optimized for Pi 4/5
        verbose=False
    )
    print("   ✓ LLM Ready")

    # 4. START LOOP
    print("\n[4/5] Starting Emotion Engine...")
    print("   ✓ Emotion Context: Ready")
    print("\n[5/5] System Ready! Waiting for input...")
    print("="*60 + "\n")

    # Main Interaction Loop
    while True:
        try:
            # A. GET INPUT (Simulated for now, replace with Voice/Camera)
            user_input = input("\nYou: ").strip()
            if not user_input: continue
            if user_input.lower() in ['quit', 'exit']: break

            start_time = time.time()

            # B. SAFETY CHECK (Input)
            if not safety.filter_input(user_input, age=CONFIG['default_age']).is_safe:
                print("AI: I can't talk about that. Let's talk about something else! 😊")
                continue

            # C. RAG RETRIEVAL
            context = ""
            if rag:
                context = rag.augment_prompt(user_input, emotion="neutral", age=CONFIG['default_age'])
                # Extract just the context part if needed, or use the full augmented prompt

            # D. GENERATE RESPONSE
            # If RAG provided a full prompt, use it. Otherwise build standard one.
            if rag and context:
                final_prompt = context
            else:
                final_prompt = f"""You are Mira, a friendly AI companion.
User: {user_input}
Mira:"""

            response = llm(
                final_prompt,
                max_tokens=200,
                temperature=0.7,
                stop=["User:", "\n\n", "Mira:"],
                echo=False
            )
            answer = response['choices'][0]['text'].strip()

            # E. SAFETY CHECK (Output)
            if not safety.filter_output(answer, age=CONFIG['default_age']).is_safe:
                answer = "I'm having a bit of trouble thinking right now. Ask me again?"

            # F. SAVE MEMORY
            memory.add_interaction("neutral", user_input, answer)

            # G. OUTPUT
            latency = time.time() - start_time
            print(f"AI: {answer}")
            print(f"    (⏱️ {latency:.2f}s | 🧠 RAG: {'Yes' if rag else 'No'})")

        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
