"""
RAG-powered chat with 2-bit LLM for fast, accurate responses.
Combines knowledge retrieval with emotion-aware generation.
"""

import sys
from pathlib import Path

print("="*60)
print("RAG + 2-BIT LLM CHAT")
print("Fast responses with accurate knowledge!")
print("="*60)

# Check for model
models_dir = Path("models")
model_files = list(models_dir.glob("*.gguf")) if models_dir.exists() else []

if not model_files:
    print("\n❌ No model found!")
    print("Download a model first:")
    print("  python download_2bit.py")
    sys.exit(1)

# Prefer 2-bit for speed
model_path = None
for model_file in model_files:
    if "Q2" in model_file.name:
        model_path = model_file
        break

if not model_path:
    model_path = model_files[0]

print(f"\n🚀 Using model: {model_path.name}")

# Initialize RAG
print("\nInitializing RAG system...")
try:
    from rag_system import RAGSystem
    rag = RAGSystem()
    print(f"✓ RAG ready: {rag.collection.count()} documents")
except Exception as e:
    print(f"⚠ RAG not available: {e}")
    print("  Running without RAG (LLM only)")
    rag = None

# Initialize LLM
print("\nLoading LLM...")
try:
    from llama_cpp import Llama
except ImportError:
    print("Installing llama-cpp-python...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "llama-cpp-python"])
    from llama_cpp import Llama

llm = Llama(
    model_path=str(model_path),
    n_ctx=2048,
    n_threads=4,
    verbose=False
)
print("✓ LLM loaded!")

# Initialize safety filter and memory
try:
    from safety_filter import SafetyFilter
    from memory_manager import MemoryManager
    
    safety = SafetyFilter()
    memory = MemoryManager(storage_path="rag_chat_memory.json")
    print("✓ Safety and memory loaded!")
except Exception as e:
    print(f"⚠ Safety/Memory not available: {e}")
    safety = None
    memory = None

print("\n" + "="*60)
print("CHAT MODE - RAG + 2-BIT LLM")
print("="*60)
print("Commands:")
print("  /rag on/off - Toggle RAG")
print("  /stats      - Show statistics")
print("  /quit       - Exit")
print("="*60 + "\n")

# Chat state
use_rag = rag is not None
message_count = 0
rag_hits = 0

while True:
    try:
        question = input("You: ").strip()
        
        if not question:
            continue
        
        # Commands
        if question.lower() in ['/quit', '/exit']:
            print("\nGoodbye! 👋")
            break
        
        if question.lower().startswith('/rag'):
            if 'on' in question.lower():
                use_rag = True if rag else False
                print(f"✓ RAG: {'ON' if use_rag else 'OFF (not available)'}")
            elif 'off' in question.lower():
                use_rag = False
                print("✓ RAG: OFF")
            continue
        
        if question.lower() == '/stats':
            print(f"\n📊 Stats:")
            print(f"  Model: {model_path.name}")
            print(f"  RAG: {'ON' if use_rag else 'OFF'}")
            print(f"  Messages: {message_count}")
            print(f"  RAG hits: {rag_hits}")
            if rag:
                print(f"  Knowledge base: {rag.collection.count()} docs")
            print()
            continue
        
        # Safety check
        if safety:
            safety_result = safety.filter_input(question, age=9)
            if not safety_result.is_safe:
                print(f"\nAI: {safety.get_refusal_response(safety_result.severity, 9)}\n")
                continue
        
        # Build prompt
        if use_rag and rag:
            # RAG-augmented prompt
            prompt = rag.augment_prompt(question, emotion="neutral", age=9)
            rag_hits += 1
        else:
            # Simple prompt
            prompt = f"""You are Mira, a friendly AI assistant for children.

User: {question}

Mira:"""
        
        # Generate response
        response = llm(
            prompt,
            max_tokens=200,
            temperature=0.7,
            stop=["User:", "\nUser", "\n\n"],
            echo=False
        )
        
        answer = response['choices'][0]['text'].strip()
        
        # Safety check output
        if safety:
            output_check = safety.filter_output(answer, age=9)
            if not output_check.is_safe:
                answer = "I'm not sure how to answer that. Can you ask something else?"
        
        print(f"\nAI: {answer}\n")
        message_count += 1
        
        # Save to memory
        if memory:
            memory.add_interaction("neutral", question, answer)
        
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
        break
    except Exception as e:
        print(f"\n⚠ Error: {e}\n")
        continue

# Final stats
print("\n" + "="*60)
print("SESSION SUMMARY")
print("="*60)
print(f"Messages: {message_count}")
print(f"RAG-augmented: {rag_hits}")
print(f"Accuracy boost: {rag_hits/message_count*100:.0f}%" if message_count > 0 else "N/A")
print("="*60)
